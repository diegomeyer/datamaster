from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_date
import json
from pyspark.sql.types import *
# Inicializar a sessão Spark
spark = SparkSession.builder \
    .appName("KafkaToBronzeLake") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
    .config("spark.yarn.queue", "root.default") \
    .getOrCreate()

KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'
KAFKA_TOPIC = 'matchs'
BRONZE_PATH = "hdfs://hadoop-namenode:8020/datalake/bronze/matchs"

# Ler dados do Kafka usando Spark Structured Streaming
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("failOnDataLoss", "false") \
    .option("startingOffsets", "earliest") \
    .load()

schema = StructType([
    StructField("timestamp_summoner", StringType(), True),
    StructField("timestamp_summoner_details", StringType(), True),
    StructField("timestamp_match", StringType(), True),
    StructField("match_details", StringType(), True),
])
# Conversão das mensagens de Kafka para o esquema definido
df_parsed = df.select(
    from_json(col("value").cast("string"), schema).alias("data")
).select("data.*")

# Adiciona a coluna de partição com a data atual
df_partitioned = df_parsed.withColumn("date", current_date())

# df_parsed.show(1,False)
# Seleciona somente as colunas necessárias
df_final = df_partitioned.select(
    "timestamp_summoner",
    "timestamp_summoner_details",
    "timestamp_match",
    "match_details",
    "date"
)

# Escrever os dados brutos na camada Bronze do Data Lake
query = (df_final.writeStream \
    .outputMode("append") \
    .format("parquet") \
    .option("checkpointLocation", "hdfs://hadoop-namenode:8020/datalake/checkpoints/matchs") \
    .partitionBy("date") \
    .option("path", BRONZE_PATH) \
    .start())

query.awaitTermination()