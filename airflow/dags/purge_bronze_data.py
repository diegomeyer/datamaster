from pyspark.sql import SparkSession
from datetime import datetime, timedelta
from pyspark.sql.utils import AnalysisException


def purge_old_partitions(spark_session, base_path, retention_days):
    """
    Deleta partições no HDFS mais antigas que o período de retenção especificado.

    :param spark_session: A SparkSession ativa.
    :param base_path: O caminho base no HDFS para os dados particionados (ex: /datalake/bronze/facebook).
    :param retention_days: Número de dias para reter os dados.
    """

    # Obter a configuração do Hadoop da SparkSession
    hadoop_conf = spark_session._jsc.hadoopConfiguration()
    print(hadoop_conf)
    # Criar um objeto URI a partir do base_path
    uri = spark_session._jvm.java.net.URI(base_path)
    print(uri)
    # Obter a instância do FileSystem para o URI especificado
    fs = spark_session._jvm.org.apache.hadoop.fs.FileSystem.get(uri, hadoop_conf)

    path_obj = spark_session._jvm.org.apache.hadoop.fs.Path(base_path)

    cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
    print(f"Caminho base para expurgo: {base_path}")
    print(
        f"Retendo dados dos últimos {retention_days} dias. Partições anteriores a {cutoff_date.strftime('%Y-%m-%d')} serão excluídas.")

    if not fs.exists(path_obj):
        print(f"Caminho base {base_path} não existe. Nada a fazer.")
        return

    try:
        # Lista todos os subdiretórios (que devem ser as partições de data)
        status = fs.listStatus(path_obj)
        for file_status in status:
            print(file_status)
            if file_status.isDirectory():
                dir_name = file_status.getPath().getName()  # Ex: "ingestion_date=YYYY-MM-DD"
                if dir_name.startswith("ingestion_date="):
                    try:
                        partition_date_str = dir_name.split("=")[1]
                        partition_date = datetime.strptime(partition_date_str, "%Y-%m-%d")
                        print(partition_date)
                        if partition_date < cutoff_date:
                            partition_path_to_delete = file_status.getPath()
                            print(f"Deletando partição antiga: {partition_path_to_delete.toString()}")
                            fs.delete(partition_path_to_delete, True)  # True para deleção recursiva
                        else:
                            print(f"Mantendo partição: {dir_name}")
                    except ValueError:
                        print(f"Não foi possível parsear a data do nome do diretório: {dir_name}")
                    except Exception as e_inner:
                        print(f"Erro ao processar partição {dir_name}: {e_inner}")
    except Exception as e:
        print(f"Erro ao listar status para {base_path}: {e}")


if __name__ == "__main__":
    spark = SparkSession.builder \
        .appName("BronzeDataPurger") \
        .getOrCreate()

    # Defina seus caminhos base e políticas de retenção
    bronze_sources = {
        "facebook": "hdfs://hadoop-namenode:8020/datalake/bronze/facebook",
        "instagram": "hdfs://hadoop-namenode:8020/datalake/bronze/instagram",
        "x": "hdfs://hadoop-namenode:8020/datalake/bronze/x"
    }
    RETENTION_DAYS_BRONZE = 30 # Exemplo: reter dados por 30 dias

    for source_name, source_path in bronze_sources.items():
        print(f"\nIniciando expurgo para a fonte: {source_name}")
        purge_old_partitions(spark, source_path, RETENTION_DAYS_BRONZE)

    spark.stop()