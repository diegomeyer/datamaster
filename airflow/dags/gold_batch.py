from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    to_date, count, sum, size, col, hour
)

spark = SparkSession.builder \
    .appName("SocialMediaGold") \
    .getOrCreate()

# Caminho da Silver
silver_path = "hdfs://hadoop-namenode:8020/datalake/silver/social_media/*"

# Lê a tabela Silver
silver_df = spark.read.parquet(silver_path)

# ==========================
# Tabela 1: Engajamento Diário por Plataforma
# ==========================
engajamento_df = silver_df.withColumn("post_day", to_date("post_date")).groupBy("source", "post_day").agg(
    count("*").alias("total_posts"),
    sum("likes").alias("total_likes"),
    sum("shares").alias("total_shares"),
    sum(size("comments")).alias("total_comments")
)

# Salva no HDFS
engajamento_df.coalesce(1).write.mode("overwrite").partitionBy("source", "post_day").parquet(
    "hdfs://hadoop-namenode:8020/datalake/gold/social_media/engajamento_diario"
)

# ==========================
# Tabela 2: Top Autores com Mais Engajamento
# ==========================
top_autores_df = silver_df.groupBy("author", "source").agg(
    count("*").alias("post_count"),
    sum("likes").alias("likes_total"),
    sum("shares").alias("shares_total"),
    sum(size("comments")).alias("comments_total")
).withColumn(
    "total_engajamento", col("likes_total") + col("shares_total") + col("comments_total")
).orderBy(col("total_engajamento").desc())

top_autores_df.coalesce(1).write.mode("overwrite").partitionBy("source").parquet(
    "hdfs://hadoop-namenode:8020/datalake/gold/social_media/top_autores"
)

# ==========================
# Tabela 3: Distribuição Horária de Posts
# ==========================
post_por_hora_df = silver_df.withColumn("hour", hour("post_date")).groupBy("source", "hour").agg(
    count("*").alias("total_posts")
).orderBy("source", "hour")

post_por_hora_df.coalesce(1).write.mode("overwrite").partitionBy("source").parquet(
    "hdfs://hadoop-namenode:8020/datalake/gold/social_media/posts_por_hora"
)

spark.stop()