import argparse
import base64
import secrets
from datetime import datetime
from typing import List, Dict, Callable

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    lit, col, to_timestamp, transform, struct, sha2, concat, current_timestamp, max as spark_max
)

from spark_utils import get_spark_session


# --- Responsabilidade 1: Funções de Transformação Puras (Uma por fonte) ---
# Cada função tem a única responsabilidade de transformar um DataFrame de uma fonte específica.
def transform_facebook(df: DataFrame) -> DataFrame:
    """Transforma o DataFrame do Facebook para o schema Silver unificado."""
    return df.select(
        col("user_name").alias("author"),
        col("post_content").alias("content"),
        to_timestamp("created_at").alias("post_date"),
        col("likes"),
        col("comments"),
        col("shares")
    ).withColumn("source", lit("facebook"))

def transform_instagram(df: DataFrame) -> DataFrame:
    """Transforma o DataFrame do Instagram para o schema Silver unificado."""
    return df.select(
        col("user_handle").alias("author"),
        col("caption").alias("content"),
        to_timestamp("posted_at").alias("post_date"),
        col("likes"),
        col("comments"),
        lit(None).cast("int").alias("shares")  # Garante a coluna 'shares' para a união
    ).withColumn("source", lit("instagram"))

def transform_x(df: DataFrame) -> DataFrame:
    """Transforma o DataFrame do X/Twitter para o schema Silver unificado."""
    df_transformed = df.select(
        col("username").alias("author"),
        col("tweet").alias("content"),
        to_timestamp("created_at").alias("post_date"),
        col("likes"),
        col("replies").alias("comments"),
        col("retweets").alias("shares")
    ).withColumn("source", lit("twitter"))

    # Estrutura aninhada de comentários
    return df_transformed.withColumn(
        "comments",
        transform(
            "comments",
            lambda c: struct(
                c["username"].alias("user"),
                c["tweet"].alias("comment"),
                c["created_at"].alias("timestamp")
            )
        )
    )

# --- Responsabilidade 2: Processamento de PII ---
def anonymize_authors(df: DataFrame) -> DataFrame:
    """Aplica hashing com salt nos autores para anonimização."""
    salt_bytes = secrets.token_bytes(32)
    salt = base64.b64encode(salt_bytes).decode('utf-8')
    return df.withColumn("author", sha2(concat(lit(salt), col("author")), 256))

# --- Responsabilidade 3: Orquestração do Job ---
class SilverProcessor:
    """Orquestra o processo de leitura, transformação e escrita para a camada Silver."""

    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.silver_table = "hadoop.silver.social_media"
        # self.processing_date = processing_date
        # OCP: Para adicionar uma nova fonte, basta adicionar uma entrada neste dicionário.
        self.source_configs: Dict[str, Dict[str, any]] = {
            "facebook": {"table": "hadoop.bronze.facebook_posts", "transformer": transform_facebook},
            "instagram": {"table": "hadoop.bronze.instagram_posts", "transformer": transform_instagram},
            "x": {"table": "hadoop.bronze.x_posts", "transformer": transform_x},
        }

    def _get_last_processed_timestamp(self) -> str:
        """Busca o último timestamp de processamento da tabela Silver."""
        try:
            # Verifica se a tabela existe antes de tentar ler
            if not self.spark.catalog.tableExists(self.silver_table):
                print(f"Tabela Silver '{self.silver_table}' não encontrada. Usando timestamp inicial padrão.")
                return "1970-01-01 00:00:00"

            print(f"Buscando último timestamp processado da tabela '{self.silver_table}'...")
            last_timestamp = self.spark.table(self.silver_table).select(spark_max("processing_timestamp")).collect()[0][
                0]
            if last_timestamp:
                print(f"Último timestamp encontrado: {last_timestamp}")
                return str(last_timestamp)
            else:
                # Caso a tabela exista mas esteja vazia
                print("Tabela Silver está vazia. Usando timestamp inicial padrão.")
                return "1970-01-01 00:00:00"
        except Exception as e:
            print(f"Erro ao buscar último timestamp. Usando padrão. Erro: {e}")
            return "1970-01-01 00:00:00"

    def _read_bronze_data(self, table_name: str, start_timestamp: str, end_timestamp: str) -> DataFrame:
        """Lê dados da camada Bronze para a data de processamento especificada."""
        print(f"Lendo da tabela '{table_name}' entre '{start_timestamp}' e '{end_timestamp}'...")
        return self.spark.table(table_name).filter(
            (col("processing_timestamp") > lit(start_timestamp).cast("timestamp")) &
            (col("processing_timestamp") <= lit(end_timestamp).cast("timestamp"))
        )

    def run(self):
        """Executa o pipeline completo de Bronze para Silver."""

        """Executa o pipeline completo de Bronze para Silver."""
        start_timestamp = self._get_last_processed_timestamp()
        # O timestamp final é o momento exato em que este job começou
        end_timestamp_df = self.spark.sql("SELECT current_timestamp() as now")
        end_timestamp = end_timestamp_df.collect()[0]['now']

        transformed_dfs: List[DataFrame] = []

        for source, config in self.source_configs.items():
            try:
                bronze_df = self._read_bronze_data(config["table"], start_timestamp, str(end_timestamp))
                if bronze_df.rdd.isEmpty():
                    print(f"Nenhum dado novo para a fonte {source} no intervalo de tempo.")
                    continue

                transformer: Callable[[DataFrame], DataFrame] = config["transformer"]
                transformed_df = transformer(bronze_df)
                transformed_dfs.append(transformed_df)
                print(transformed_df.count())
            except Exception as e:
                print(f"AVISO: Falha ao processar a fonte {source}. Erro: {e}")

        if not transformed_dfs:
            print("Nenhum dado processado de nenhuma fonte. Finalizando o job.")
            return

        # Unifica todos os DataFrames transformados
        unified_df = transformed_dfs[0]
        for df in transformed_dfs[1:]:
            unified_df = unified_df.unionByName(df, allowMissingColumns=True)

        # Aplica transformações finais e escreve
        final_df = anonymize_authors(unified_df)
        final_df = final_df.withColumn("processing_timestamp", lit(end_timestamp))\
                   .withColumn("ingestion_date", col("processing_timestamp").cast("date"))
        print(final_df.count())
        print("Gravando dados unificados na camada Silver...")
        final_df.write \
            .format("iceberg") \
            .mode("append") \
            .partitionBy("ingestion_date") \
            .saveAsTable("hadoop.silver.social_media")
        print("Dados gravados com sucesso na camada Silver.")


def main():
    """Ponto de entrada do script."""
    spark = get_spark_session("SocialMediaSilver")

    processor = SilverProcessor(spark)
    processor.run()

    spark.stop()

if __name__ == "__main__":
    main()