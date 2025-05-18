import secrets
import base64

from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, col, to_timestamp, transform, struct, sha2, concat
from datetime import datetime, timedelta
spark = SparkSession.builder \
    .appName("SocialMediaSilver") \
    .getOrCreate()


current_time = datetime.utcnow()
window_start = current_time - timedelta(minutes=10)
window_end = current_time

# substitui df vazio por um DataFrame vazio com schema esperado
def empty_df():
    empty_schema = StructType([
        StructField("author", StringType(), True),
        StructField("content", StringType(), True),
        StructField("post_date", TimestampType(), True),
        StructField("likes", IntegerType(), True),
        StructField("comments", ArrayType(StructType([
            StructField("user", StringType(), True),
            StructField("comment", StringType(), True),
            StructField("timestamp", StringType(), True)
        ])), True),
        StructField("shares", IntegerType(), True),
        StructField("source", StringType(), True)
    ])
    return spark.createDataFrame([], empty_schema)

# Função para carregar e transformar cada fonte
def process_social_data(path, source):
    # Define a janela de 10 minutos
    df = spark.read.parquet(path).filter(
        (col("event_time") >= window_start.isoformat()) &
        (col("event_time") < window_end.isoformat())
    )
    if df.isEmpty():
        return empty_df()
    else:
        if source == "facebook":
            return df.select(
                col("user_name").alias("author"),
                col("post_content").alias("content"),
                to_timestamp("created_at").alias("post_date"),
                col("likes").alias("likes"),
                col("comments").alias("comments"),
                col("shares").alias("shares"),
            ).withColumn("source", lit("facebook"))

        elif source == "instagram":
            return df.select(
                col("user_handle").alias("author"),
                col("caption").alias("content"),
                to_timestamp("posted_at").alias("post_date"),
                col("likes").alias("likes"),
                col("comments").alias("comments"),
                lit(None).cast("int").alias("shares")
            ).withColumn("source", lit("instagram"))

        elif source == "x":
            df = df.select(
                col("username").alias("author"),
                col("tweet").alias("content"),
                to_timestamp("created_at").alias("post_date"),
                col("likes").alias("likes"),
                col("replies").alias("comments"),
                col("retweets").alias("shares")
            ).withColumn("source", lit("twitter"))
            #Tratando normalização comentarios
            df = df.withColumn(
                "comments",
                transform("comments", lambda c: struct(
                    c["username"].alias("user"),
                    c["tweet"].alias("comment"),
                    c["created_at"].alias("timestamp")
                ))
            )
            return df

# Paths da Bronze
facebook_df = process_social_data("hdfs://hadoop-namenode:8020/datalake/bronze/facebook", "facebook")
instagram_df = process_social_data("hdfs://hadoop-namenode:8020/datalake/bronze/instagram", "instagram")
x_df = process_social_data("hdfs://hadoop-namenode:8020/datalake/bronze/x", "x")

# União e escrita na camada Silver
silver_df = facebook_df.unionByName(instagram_df).unionByName(x_df)

# *** GERAÇÃO DE UM SALT ALEATÓRIO E SEGURO ***
salt_bytes = secrets.token_bytes(32)  # Gera 32 bytes aleatórios
salt = base64.b64encode(salt_bytes).decode('utf-8') # Codifica para uma string base64 para facilitar o armazenamento

# *** APLICAÇÃO DA FUNÇÃO DE HASHING COM O SALT ALEATÓRIO ***
silver_df.withColumn("author", sha2(concat(lit(salt), "username"), 256))

silver_df.coalesce(1).write.mode("append").parquet("hdfs://hadoop-namenode:8020/datalake/silver/social_media/")
