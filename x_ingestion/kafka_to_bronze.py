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
# CREATE TABLE IF NOT EXISTS bronze.x_posts (
#     username STRING,
#     display_name STRING,
#     tweet STRING,
#     created_at STRING,
#     likes INT,
#     retweets INT,
#     verified BOOLEAN,
#     replies ARRAY<STRUCT<
#         username: STRING,
#         tweet: STRING,
#         created_at: STRING
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
    .option("subscribe", 'x-post') \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()


replies_schema = StructType([
    StructField("username", StringType(), True),
    StructField("tweet", StringType(), True),
    StructField("created_at", StringType(), True)
])

x_schema = StructType([
    StructField("username", StringType(), True),
    StructField("display_name", StringType(), True),
    StructField("tweet", StringType(), True),
    StructField("created_at", StringType(), True),
    StructField("likes", IntegerType(), True),
    StructField("retweets", IntegerType(), True),
    StructField("verified", BooleanType(), True),
    StructField("replies", ArrayType(replies_schema), True)
])


# Extração e parsing do JSON
df_parsed = df_raw.selectExpr("CAST(value AS STRING) as json") \
    .withColumn("data", from_json(col("json"), x_schema)) \
    .select("data.*")
df_parsed = df_parsed.withColumn("event_time", current_timestamp())\
    .withColumn("ingestion_date", date_format(col("event_time"), "yyyy-MM-dd"))

table_name = "hadoop.bronze.x_posts"
# Escrever os dados brutos na camada Bronze do Data Lake
query = df_parsed.writeStream \
    .format("iceberg") \
    .partitionBy("ingestion_date")\
    .outputMode("append") \
    .trigger(processingTime="10 minutes")\
    .option("checkpointLocation", f"s3a://{s3_bucket_name}/spark_checkpoint/x/") \
    .toTable(table_name)

query.awaitTermination()