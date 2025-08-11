import argparse
import base64
import secrets
from datetime import datetime
from typing import List, Dict, Callable

from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import (
    lit, col, to_timestamp, transform, struct, sha2, concat
)
from pyspark.sql.types import (
    StructType, StructField, StringType, TimestampType, IntegerType, ArrayType
)

from spark_utils import get_spark_session


def small_files_batch(spark: SparkSession, catalog_name: str, tables: List[str]):
    for table in tables:
        print(f"Processando tabela: {table}")
        rewrite_sql = f"""
            CALL {catalog_name}.system.rewrite_data_files(
                table => '{table}',
                options => map('min-input-files', '5', 'target-file-size-bytes', '134217728')
            )
        """

        result_df = spark.sql(rewrite_sql)
        result_df.show(truncate=False)
        print("'rewrite_data_files' concluído com sucesso.")


def main():
    spark = get_spark_session("Compact Iceberg Small Files Batch")

    tables = [
        'hadoop.bronze.instagram_posts',
        'hadoop.bronze.facebook_posts',
        'hadoop.bronze.x_posts',
        'hadoop.silver.social_media',
        'hadoop.gold.engajamento_diario',
        'hadoop.gold.top_autores',
        'hadoop.gold.posts_por_hora',
    ]
    small_files_batch(spark, 'hadoop', tables)

    spark.stop()

if __name__ == "__main__":
    main()