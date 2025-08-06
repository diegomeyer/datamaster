import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_date, current_timestamp, date_format
import json
from pyspark.sql.types import *

access_key = os.getenv("access_key")
secret_key = os.getenv("secret_key")
kafka_bootstrap_servers =  os.getenv("KAFKA_BOOTSTRAP_SERVERS")


s3_bucket_name = "warehouse"
output_path = f"s3a://{s3_bucket_name}/bronze/facebook/" # Caminho de saída no MinIO



# Inicializar a sessão Spark
spark = SparkSession.builder \
    .appName("FacebookStreaming") \
    .config("spark.jars.packages",
            "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.1,org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0,org.apache.hadoop:hadoop-aws:3.3.2,org.apache.iceberg:iceberg-aws-bundle:1.4.1") \
    .config("spark.sql.catalog.hadoop", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.hadoop.type", "hadoop") \
    .config("spark.sql.catalog.hadoop.warehouse", "s3a://warehouse/") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.secret.key", "minioadmin") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .getOrCreate()

# spark.sql("CREATE NAMESPACE IF NOT EXISTS hadoop.bronze").show()
# spark.sql("""
# CREATE TABLE IF NOT EXISTS bronze.facebook_posts (
#     id STRING,
#     user_name STRING,
#     post_content STRING,
#     created_at STRING,
#     likes INT,
#     shares INT,
#     comments ARRAY<STRUCT<
#         user: STRING,
#         comment: STRING,
#         timestamp: STRING
#     >>,
#     event_time TIMESTAMP,
#     ingestion_date STRING
# )
# USING iceberg
# PARTITIONED BY (ingestion_date)
# """).show()

# Leitura do tópico Kafka
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", 'facebook-post') \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()

# Schema do JSON enviado
comment_schema = StructType([
    StructField("user", StringType(), True),
    StructField("comment", StringType(), True),
    StructField("timestamp", StringType(), True)
])

message_schema = StructType([
    StructField("id", StringType(), True),
    StructField("user_name", StringType(), True),
    StructField("post_content", StringType(), True),
    StructField("created_at", StringType(), True),
    StructField("likes", IntegerType(), True),
    StructField("shares", IntegerType(), True),
    StructField("comments", ArrayType(comment_schema), True)
])

df_parsed = df_raw.selectExpr("CAST(value AS STRING) as json") \
    .withColumn("data", from_json(col("json"), message_schema)) \
    .select("data.*")
df_parsed = df_parsed.withColumn("event_time", current_timestamp())\
    .withColumn("ingestion_date", date_format(col("event_time"), "yyyy-MM-dd"))

table_name = "hadoop.bronze.facebook_posts"
# Escrever os dados brutos na camada Bronze do Data Lake
query = df_parsed.writeStream \
    .format("iceberg") \
    .partitionBy("ingestion_date")\
    .outputMode("append") \
    .trigger(processingTime="10 minutes")\
    .option("checkpointLocation", f"s3a://{s3_bucket_name}/spark_checkpoint/facebook/") \
    .toTable(table_name)

query.awaitTermination()