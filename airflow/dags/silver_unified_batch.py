import secrets
import base64
from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, col, to_timestamp, transform, struct, sha2, concat, date_format, current_date
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, IntegerType, ArrayType
from datetime import datetime, timedelta

spark = SparkSession.builder \
    .appName("SocialMediaSilver") \
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

current_time = datetime.utcnow()
window_start = current_time - timedelta(minutes=60) # Janela aumentada para garantir dados
window_end = current_time
date_start_str = window_start.strftime('%Y-%m-%d')
date_end_str = window_end.strftime('%Y-%m-%d')

print(f"Janela de processamento Silver: {window_start.isoformat()} a {window_end.isoformat()}")

def empty_df():
    # ... (código da função inalterado)
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

def process_social_data(table, source):
    try:
        # A tabela é chamada com 2 partes (schema.tabela) e o catálogo padrão será usado
        df_reader = spark.table(table).filter(
            (col("event_time") >= window_start.isoformat()) &
            (col("event_time") < window_end.isoformat())
        )
        if date_start_str == date_end_str:
            df_reader = df_reader.where(col("ingestion_date") == date_start_str)
        else:
            df_reader = df_reader.where(col("ingestion_date").between(date_start_str, date_end_str))
        if not df_reader.head(1):
            print(f"Nenhum dado novo para a fonte {source}.")
            return empty_df()
        df = df_reader
        if source == "facebook":
            return df.select(col("user_name").alias("author"), col("post_content").alias("content"), to_timestamp("created_at").alias("post_date"), col("likes"), col("comments"), col("shares")).withColumn("source", lit("facebook"))
        elif source == "instagram":
            return df.select(col("user_handle").alias("author"), col("caption").alias("content"), to_timestamp("posted_at").alias("post_date"), col("likes"), col("comments"), lit(None).cast("int").alias("shares")).withColumn("source", lit("instagram"))
        elif source == "x":
            df = df.select(col("username").alias("author"), col("tweet").alias("content"), to_timestamp("created_at").alias("post_date"), col("likes"), col("replies").alias("comments"), col("retweets").alias("shares")).withColumn("source", lit("twitter"))
            df = df.withColumn("comments", transform("comments", lambda c: struct(c["username"].alias("user"), c["tweet"].alias("comment"), c["created_at"].alias("timestamp"))))
            return df
    except Exception as e:
        print(f"Erro ao processar {source} ({table}): {e}")
        return empty_df()

# Ler dados
facebook_df = process_social_data("hadoop.bronze.facebook_posts", "facebook")
instagram_df = process_social_data("hadoop.bronze.instagram_posts", "instagram")
x_df = process_social_data("hadoop.bronze.x_posts", "x")

# Unir e gravar
silver_df = facebook_df.unionByName(instagram_df, allowMissingColumns=True).unionByName(x_df, allowMissingColumns=True)

if silver_df.head(1):
    silver_df = silver_df.withColumn("processing_date", date_format(current_date(), "yyyy-MM-dd"))
    salt_bytes = secrets.token_bytes(32)
    salt = base64.b64encode(salt_bytes).decode('utf-8')
    silver_df = silver_df.withColumn("author", sha2(concat(lit(salt), col("author")), 256))
    silver_df.write \
        .format("iceberg") \
        .mode("append") \
        .partitionBy("processing_date") \
        .saveAsTable("hadoop.silver.social_media")
    print("Dados gravados com sucesso na camada Silver.")
else:
    print("Nenhum dado novo para processar. Finalizando o job.")

spark.stop()