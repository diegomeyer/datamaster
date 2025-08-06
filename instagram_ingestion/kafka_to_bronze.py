from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, date_format, current_timestamp
import os
from pyspark.sql.types import *

access_key = os.getenv("access_key")
secret_key = os.getenv("secret_key")
kafka_bootstrap_servers =  os.getenv("KAFKA_BOOTSTRAP_SERVERS")


s3_bucket_name = "warehouse"

# Inicializar a sessão Spark
spark = SparkSession.builder \
    .appName("InstagramStreaming") \
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
# CREATE TABLE IF NOT EXISTS bronze.instagram_posts (
#     id STRING,
#     user_handle STRING,
#     caption STRING,
#     image_url STRING,
#     posted_at STRING,
#     likes INT,
#     hashtags ARRAY<STRING>,
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
    .option("subscribe", 'instagram-post') \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()

comment_schema = StructType([
    StructField("user", StringType(), True),
    StructField("comment", StringType(), True),
    StructField("timestamp", StringType(), True)
])
# Schema do JSON enviado
instagram_schema = StructType([
    StructField("id", StringType(), True),
    StructField("user_handle", StringType(), True),
    StructField("caption", StringType(), True),
    StructField("image_url", StringType(), True),
    StructField("posted_at", StringType(), True),  # ou TimestampType se já estiver parseado
    StructField("likes", IntegerType(), True),
    StructField("hashtags", ArrayType(StringType()), True),
    StructField("comments", ArrayType(comment_schema), True)
])


# Extração e parsing do JSON
df_parsed = df_raw.selectExpr("CAST(value AS STRING) as json") \
    .withColumn("data", from_json(col("json"), instagram_schema)) \
    .select("data.*")
df_parsed = df_parsed.withColumn("event_time", current_timestamp())\
    .withColumn("ingestion_date", date_format(col("event_time"), "yyyy-MM-dd"))

table_name = "hadoop.bronze.instagram_posts"
# Escrever os dados brutos na camada Bronze do Data Lake
query = df_parsed.writeStream \
    .format("iceberg") \
    .partitionBy("ingestion_date")\
    .outputMode("append") \
    .trigger(processingTime="10 minutes")\
    .option("checkpointLocation", f"s3a://{s3_bucket_name}/spark_checkpoint/instagram/") \
    .toTable(table_name)

query.awaitTermination()