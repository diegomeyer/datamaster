import argparse
from typing import Dict, List, Callable
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import to_date, count, sum, size, col, hour

from spark_utils import get_spark_session


# --- Responsabilidade 1: Funções de Agregação Puras ---
# Cada função tem a única responsabilidade de calcular uma métrica de negócio.
# Elas recebem um DataFrame e retornam um DataFrame, tornando-as testáveis.

def calculate_daily_engagement(df: DataFrame) -> DataFrame:
    """Calcula o engajamento diário por plataforma."""
    return df.withColumn("post_day", to_date("post_date")).groupBy("source", "post_day").agg(
        count("*").alias("total_posts"),
        sum("likes").alias("total_likes"),
        sum("shares").alias("total_shares"),
        sum(size("comments")).alias("total_comments")
    )


def calculate_top_authors(df: DataFrame) -> DataFrame:
    """Calcula os autores com maior engajamento total."""
    return df.groupBy("author", "source").agg(
        count("*").alias("post_count"),
        sum("likes").alias("likes_total"),
        sum("shares").alias("shares_total"),
        sum(size("comments")).alias("comments_total")
    ).withColumn(
        "total_engagement", col("likes_total") + col("shares_total") + col("comments_total")
    ).orderBy(col("total_engagement").desc())


def calculate_hourly_distribution(df: DataFrame) -> DataFrame:
    """Calcula a distribuição de posts por hora para cada plataforma."""
    return df.withColumn("hour", hour("post_date")).groupBy("source", "hour").agg(
        count("*").alias("total_posts")
    ).orderBy("source", "hour")


# --- Responsabilidade 2: Orquestração do Job ---

class GoldProcessor:
    """Orquestra o processo de leitura, agregação e escrita para a camada Gold."""

    def __init__(self, spark: SparkSession, processing_date: str):
        self.spark = spark
        self.processing_date = processing_date
        self.silver_df = self._read_silver_data()

        # OCP: Para adicionar uma nova agregação, basta adicionar uma entrada neste dicionário.
        # O código do método `run` não precisa ser modificado.
        self.aggregations_config: Dict[str, Dict] = {
            "daily_engagement": {
                "calculator": calculate_daily_engagement,
                "partitions": ["source", "post_day"]
            },
            "top_authors": {
                "calculator": calculate_top_authors,
                "partitions": ["source"]
            },
            "hourly_posts": {
                "calculator": calculate_hourly_distribution,
                "partitions": ["source"]
            },
        }

    def _read_silver_data(self) -> DataFrame:
        """Lê os dados da camada Silver para a data de processamento especificada."""
        print(f"Lendo dados da tabela Silver para a data: {self.processing_date}")
        return self.spark.table("hadoop.silver.social_media").filter(
            col("ingestion_date") == self.processing_date
        ).cache()  # Adiciona cache para otimizar, já que o DF será lido várias vezes

    def run(self):
        """Executa todas as agregações e salva os resultados nas tabelas Gold."""
        if self.silver_df.rdd.isEmpty():
            print(f"Nenhum dado na camada Silver para a data {self.processing_date}. Finalizando.")
            return

        for name, config in self.aggregations_config.items():
            print(f"Calculando e salvando a tabela Gold: {name}")

            # Pega a função de cálculo e o DataFrame de entrada
            calculator_func: Callable[[DataFrame], DataFrame] = config["calculator"]
            gold_df = calculator_func(self.silver_df)

            # Escreve o resultado
            gold_df.write \
                .format("iceberg") \
                .mode("overwrite") \
                .partitionBy(*config["partitions"]) \
                .saveAsTable(f"hadoop.gold.{name}")

        print("Processo da camada Gold finalizado com sucesso.")
        self.silver_df.unpersist()  # Libera o cache


def main():
    """Ponto de entrada do script: parseia argumentos e inicia o processador."""
    parser = argparse.ArgumentParser(description="Processa dados da Silver para a Gold.")
    parser.add_argument('--processing-date', required=True, help='Data de processamento (YYYY-MM-DD).')
    args = parser.parse_args()

    spark = get_spark_session("SocialMediaGold")

    processor = GoldProcessor(spark, args.processing_date)
    processor.run()

    spark.stop()


if __name__ == "__main__":
    main()