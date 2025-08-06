import argparse
from datetime import datetime, timedelta
from pyspark.sql import SparkSession

from spark_utils import get_spark_session


# Supondo que você tenha o get_spark_session em um utilitário
# from spark_utils import get_spark_session

def purge_iceberg_table_data(spark: SparkSession, catalog_name: str, table_name: str, retention_days: int):
    """
    Executa o expurgo de dados em uma tabela Apache Iceberg usando os procedimentos do sistema.

    :param spark: A SparkSession ativa.
    :param catalog_name: O nome do catálogo Iceberg (ex: 'hadoop').
    :param table_name: O nome completo da tabela (ex: 'silver.social_media').
    :param retention_days: Número de dias para reter os dados.
    """
    full_table_identifier = f"{catalog_name}.{table_name}"
    print(f"\n--- Iniciando expurgo para a tabela Iceberg: {full_table_identifier} ---")

    # 1. Expirar Snapshots Antigos
    # Calcula o timestamp de corte. Snapshots mais antigos que esta data serão removidos.
    cutoff_dt = datetime.utcnow() - timedelta(days=retention_days)
    cutoff_timestamp_str = cutoff_dt.strftime('%Y-%m-%d %H:%M:%S')

    print(f"Retendo dados dos últimos {retention_days} dias.")
    print(f"Expirando snapshots mais antigos que: {cutoff_timestamp_str}")

    try:
        # A query CALL invoca o procedimento do sistema Iceberg
        expire_sql = f"""
            CALL {catalog_name}.system.expire_snapshots(
                table => '{full_table_identifier}',
                older_than => TIMESTAMP '{cutoff_timestamp_str}',
                retain_last => 10
            )
        """
        print("Executando 'expire_snapshots'...")
        result_df = spark.sql(expire_sql)
        result_df.show(truncate=False)
        print("'expire_snapshots' concluído com sucesso.")

    except Exception as e:
        print(f"Erro ao executar 'expire_snapshots' para a tabela {full_table_identifier}: {e}")
        # Continua para a próxima etapa ou tabela, dependendo da sua política de falha
        return

    # 2. Deletar Arquivos Órfãos
    # Esta etapa deleta fisicamente os arquivos que não são mais referenciados por nenhum snapshot.
    print("\nIniciando a deleção de arquivos órfãos...")
    try:
        delete_sql = f"CALL {catalog_name}.system.delete_orphan_files(table => '{full_table_identifier}')"
        print("Executando 'delete_orphan_files'...")
        result_df = spark.sql(delete_sql)
        result_df.show(truncate=False)
        print("'delete_orphan_files' concluído com sucesso.")

    except Exception as e:
        print(f"Erro ao executar 'delete_orphan_files' para a tabela {full_table_identifier}: {e}")

    print(f"--- Expurgo para a tabela {full_table_identifier} finalizado. ---")


if __name__ == "__main__":
    spark = get_spark_session("SilverIcebergPurger")

    # Defina suas tabelas Silver e políticas de retenção
    CATALOG_NAME = "hadoop"
    SILVER_TABLES = [
        "bronze.facebook_posts",
        "bronze.instagram_posts",
        "bronze.x_posts"
        # Adicione outras tabelas silver aqui se necessário
    ]
    RETENTION_DAYS_SILVER = 90  # Exemplo: reter dados na camada Silver por 90 dias

    for table in SILVER_TABLES:
        purge_iceberg_table_data(spark, CATALOG_NAME, table, RETENTION_DAYS_SILVER)

    spark.stop()
