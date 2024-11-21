from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import json

# Configuração da sessão Spark
spark = SparkSession.builder \
    .appName("KafkaToBronzeLake") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.1.2") \
    .getOrCreate()

# Configuração do Kafka
KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'
KAFKA_TOPIC = 'matchs'

# Ler dados do Kafka usando Spark Structured Streaming
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
    .option("subscribe", KAFKA_TOPIC) \
    .option("startingOffsets", "latest") \
    .load()

# Converter o valor da mensagem Kafka de binário para string
df_parsed = df.selectExpr("CAST(value AS STRING) as json_data")

# Exibir dados lidos do Kafka no console para debug
query_debug = df_parsed.writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

# # Gravar os dados no Data Lake em formato Parquet
# BRONZE_PATH = "hdfs://hadoop-namenode:8020/datalake/bronze/matchs"
# query = df_parsed \
#     .writeStream \
#     .outputMode("append") \
#     .format("parquet") \
#     .option("checkpointLocation", "hdfs://hadoop-namenode:8020/datalake/checkpoints/matchs") \
#     .option("path", BRONZE_PATH) \
#     .start()

# # Manter o streaming ativo até ser interrompido
# query.awaitTermination()