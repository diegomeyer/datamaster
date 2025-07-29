from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, date_format, current_timestamp
from pyspark.sql.types import StructType, StructField, StringType, ArrayType, IntegerType
import os

kafka_bootstrap_servers = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
kafka_topic = os.environ.get("KAFKA_TOPIC", "instagram-post")

# Configurações do S3/MinIO
s3_bucket_name = "warehouse" # Nome do seu bucket no MinIO (criado pelo `mc` do docker-compose)
output_path = f"s3a://{s3_bucket_name}/bronze/instagram/" # Caminho de saída no MinIO

# Inicializar a sessão Spark
spark = SparkSession.builder \
    .appName("KafkaConsumerToS3") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.1,org.apache.hadoop:hadoop-aws:3.3.1,com.amazonaws:aws-java-sdk-bundle:1.11.901") \
        .config("spark.hadoop.fs.s3a.endpoint", "http://minio:9000") \
    .config("spark.hadoop.fs.s3a.access.key", os.environ.get("AWS_ACCESS_KEY_ID")) \
    .config("spark.hadoop.fs.s3a.secret.key", os.environ.get("AWS_SECRET_ACCESS_KEY")) \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .getOrCreate()

# Leitura do tópico Kafka
df_raw = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("subscribe", kafka_topic) \
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

# Escrever os dados brutos na camada Bronze do Data Lake
query = (df_parsed.coalesce(1).writeStream\
    .format("parquet")\
    .partitionBy("ingestion_date")\
    .option("path", output_path)\
    .option("checkpointLocation", f"s3a://{s3_bucket_name}/_spark_checkpoint/instagram/") \
    .trigger(processingTime="10 minutes")\
    .outputMode("append")\
    .start())

query.awaitTermination()