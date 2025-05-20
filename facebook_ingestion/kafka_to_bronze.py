from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_date, current_timestamp, date_format
import json
from pyspark.sql.types import *

KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'
KAFKA_TOPIC = 'facebook-post'
BRONZE_PATH = "hdfs://hadoop-namenode:8020/datalake/bronze/facebook"


# Inicializar a sessão Spark
spark = SparkSession.builder \
    .appName("KafkaToBronzeLake") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
    .getOrCreate()

# Leitura do tópico Kafka
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("subscribe", KAFKA_TOPIC) \
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

# Escrever os dados brutos na camada Bronze do Data Lake
query = (df_parsed.repartition(1).writeStream\
    .format("parquet")\
    .partitionBy("ingestion_date")\
    .option("path", BRONZE_PATH)\
    .option("checkpointLocation", "hdfs://hadoop-namenode:8020/datalake/checkpoints/facebook")\
    .trigger(processingTime="10 minutes")\
    .outputMode("append")\
    .start())

query.awaitTermination()