import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    to_date, count, sum, size, col, hour
)

def get_args():
    """Lê e parseia os argumentos da linha de comando."""
    parser = argparse.ArgumentParser(description="Processa dados da camada Silver para a Gold para uma data específica.")
    parser.add_argument(
        '--processing-date',
        required=True,
        help='A data de processamento no formato YYYY-MM-DD, fornecida pelo Airflow.'
    )
    return parser.parse_args()

def main():
    # Pega a data passada como argumento
    args = get_args()
    processing_date = args.processing_date
    print(f"Processando dados para a data: {processing_date}")
    spark = SparkSession.builder \
        .appName("SocialMediaGold") \
        .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.hadoop:hadoop-aws:3.3.2,org.apache.iceberg:iceberg-aws-bundle:1.4.1") \
        .config("spark.sql.catalog.hadoop", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.catalog.hadoop.type", "hadoop") \
        .config("spark.sql.catalog.hadoop.warehouse", "s3a://warehouse/") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .getOrCreate()

    silver_table = "hadoop.silver.social_media"

    # Lê a tabela Silver, filtrando pela data passada como argumento pelo Airflow
    # Isso substitui a lógica de `date_sub(current_date(), 1)`
    silver_df = spark.table(silver_table).filter(
        col("processing_date") == processing_date
    )

    # ==========================
    # Tabela 1: Engajamento Diário por Plataforma
    # ==========================
    engajamento_df = silver_df.withColumn("post_day", to_date("post_date")).groupBy("source", "post_day").agg(
        count("*").alias("total_posts"),
        sum("likes").alias("total_likes"),
        sum("shares").alias("total_shares"),
        sum(size("comments")).alias("total_comments")
    )

    engajamento_df.write \
        .format("iceberg") \
        .mode("overwrite") \
        .partitionBy("source", "post_day") \
        .saveAsTable("hadoop.gold.engajamento_diario")

    # ... resto do seu código de transformação e salvamento ...

    spark.stop()

if __name__ == "__main__":
    main()