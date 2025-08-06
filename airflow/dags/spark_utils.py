from pyspark.sql import SparkSession
import os

def get_spark_session(app_name: str) -> SparkSession:
    """
    Cria e retorna uma SparkSession configurada para o projeto,
    lendo as credenciais de variáveis de ambiente com valores padrão.
    """
    return SparkSession.builder \
        .appName(app_name) \
        .config("spark.jars.packages",
                "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.1,"
                "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,"
                "org.apache.hadoop:hadoop-aws:3.3.2,"
                "org.apache.iceberg:iceberg-aws-bundle:1.4.1") \
        .config("spark.sql.catalog.hadoop", "org.apache.iceberg.spark.SparkCatalog") \
        .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions")\
        .config("spark.sql.catalog.hadoop.type", "hadoop") \
        .config("spark.sql.catalog.hadoop.warehouse", "s3a://warehouse/") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
        .config("spark.hadoop.fs.s3a.access.key", os.getenv("MINIO_ROOT_USER", "minioadmin")) \
        .config("spark.hadoop.fs.s3a.secret.key", os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")) \
        .config("spark.hadoop.fs.s3a.path.style.access", "true") \
        .getOrCreate()