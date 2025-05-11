from pyspark.sql import SparkSession
from pyspark.sql.functions import lit, col, to_timestamp
from datetime import datetime, timedelta
spark = SparkSession.builder \
    .appName("SocialMediaSilver") \
    .getOrCreate()


current_time = datetime.utcnow()
window_start = current_time - timedelta(minutes=10)
window_end = current_time

# Função para carregar e transformar cada fonte
def process_social_data(path, source):
    # Define a janela de 10 minutos
    df = spark.read.parquet(path).filter(
        (col("event_time") >= window_start.isoformat()) &
        (col("event_time") < window_end.isoformat())
    )
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

    elif source == "twitter":
        return df.select(
            col("user.screen_name").alias("author"),
            col("tweet.text").alias("content"),
            to_timestamp("tweet.created_at").alias("post_date"),
            col("metrics.likes").alias("likes"),
            col("metrics.replies").alias("comments"),
            col("metrics.retweets").alias("shares")
        ).withColumn("source", lit("twitter"))


# Paths da Bronze
facebook_df = process_social_data("hdfs://hadoop-namenode:8020/datalake/bronze/facebook", "facebook")
instagram_df = process_social_data("hdfs://hadoop-namenode:8020/datalake/bronze/instagram", "instagram")
x_df = process_social_data("hdfs://hadoop-namenode:8020/datalake/bronze/x", "x")

# União e escrita na camada Silver
silver_df = facebook_df.unionByName(instagram_df).unionByName(x_df)

silver_df.coalese(1).write.mode("append").parquet("hdfs://hadoop-namenode:8020/datalake/silver/social_media/")
