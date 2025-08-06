from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType, BooleanType

# --- Definições de Schema Reutilizáveis ---

_COMMENT_SCHEMA_GENERIC = StructType([
    StructField("user", StringType(), True),
    StructField("comment", StringType(), True),
    StructField("timestamp", StringType(), True)
])

# --- Schemas Específicos por Fonte ---

FACEBOOK_SCHEMA = StructType([
    StructField("id", StringType(), True),
    StructField("user_name", StringType(), True),
    StructField("post_content", StringType(), True),
    StructField("created_at", StringType(), True),
    StructField("likes", IntegerType(), True),
    StructField("shares", IntegerType(), True),
    StructField("comments", ArrayType(_COMMENT_SCHEMA_GENERIC), True)
])

INSTAGRAM_SCHEMA = StructType([
    StructField("id", StringType(), True),
    StructField("user_handle", StringType(), True),
    StructField("caption", StringType(), True),
    StructField("image_url", StringType(), True),
    StructField("posted_at", StringType(), True),
    StructField("likes", IntegerType(), True),
    StructField("hashtags", ArrayType(StringType()), True),
    StructField("comments", ArrayType(_COMMENT_SCHEMA_GENERIC), True)
])

_X_REPLIES_SCHEMA = StructType([
    StructField("username", StringType(), True),
    StructField("tweet", StringType(), True),
    StructField("created_at", StringType(), True)
])

X_SCHEMA = StructType([
    StructField("username", StringType(), True),
    StructField("display_name", StringType(), True),
    StructField("tweet", StringType(), True),
    StructField("created_at", StringType(), True),
    StructField("likes", IntegerType(), True),
    StructField("retweets", IntegerType(), True),
    StructField("verified", BooleanType(), True),
    StructField("replies", ArrayType(_X_REPLIES_SCHEMA), True)
])

# --- Dicionário de Configuração Central ---

S3_BUCKET_NAME = "warehouse"

SOURCE_CONFIGS = {
    "facebook": {
        "kafka_topic": "facebook-post",
        "schema": FACEBOOK_SCHEMA,
        "table_name": "hadoop.bronze.facebook_posts",
        "checkpoint_location": f"s3a://{S3_BUCKET_NAME}/spark_checkpoint/facebook/"
    },
    "instagram": {
        "kafka_topic": "instagram-post",
        "schema": INSTAGRAM_SCHEMA,
        "table_name": "hadoop.bronze.instagram_posts",
        "checkpoint_location": f"s3a://{S3_BUCKET_NAME}/spark_checkpoint/instagram/"
    },
    "x": {
        "kafka_topic": "x-post",
        "schema": X_SCHEMA,
        "table_name": "hadoop.bronze.x_posts",
        "checkpoint_location": f"s3a://{S3_BUCKET_NAME}/spark_checkpoint/x/"
    }
}