# airflow/dags/tests/test_gold_aggregations.py
import pytest
from datetime import datetime
from pyspark.sql import SparkSession, Row
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, ArrayType

# Importe as funções que você quer testar
from airflow.dags.silver_to_gold_batch_refactored import (
    calculate_daily_engagement,
    calculate_top_authors
)


@pytest.fixture(scope="module")
def silver_df_fixture(spark: SparkSession) -> DataFrame:
    """Cria um DataFrame de exemplo simulando a tabela Silver para os testes."""
    schema = StructType([
        StructField("author", StringType()),
        StructField("source", StringType()),
        StructField("post_date", TimestampType()),
        StructField("likes", IntegerType()),
        StructField("shares", IntegerType()),
        StructField("comments", ArrayType(StringType())),
    ])
    data = [
        ("user_A", "facebook", datetime(2024, 5, 20, 10), 100, 10, ["c1", "c2"]),
        ("user_B", "facebook", datetime(2024, 5, 20, 11), 50, 5, ["c3"]),
        ("user_A", "instagram", datetime(2024, 5, 20, 12), 200, 0, ["c4", "c5", "c6"]),
    ]
    return spark.createDataFrame(data, schema)


def test_calculate_daily_engagement(silver_df_fixture: DataFrame):
    """
    Testa a função de cálculo de engajamento diário.
    GIVEN: Um DataFrame com dados da camada Silver.
    WHEN: A função calculate_daily_engagement é chamada.
    THEN: O DataFrame resultante deve conter as métricas de engajamento agregadas corretamente.
    """
    # Act
    result_df = calculate_daily_engagement(silver_df_fixture)
    result_data = sorted(result_df.collect(), key=lambda r: r.source)

    # Assert
    assert len(result_data) == 2

    # Facebook
    assert result_data[0]['source'] == 'facebook'
    assert result_data[0]['total_posts'] == 2
    assert result_data[0]['total_likes'] == 150
    assert result_data[0]['total_shares'] == 15
    assert result_data[0]['total_comments'] == 3  # 2 + 1

    # Instagram
    assert result_data[1]['source'] == 'instagram'
    assert result_data[1]['total_posts'] == 1
    assert result_data[1]['total_likes'] == 200
    assert result_data[1]['total_shares'] is None  # Sum of nulls is null
    assert result_data[1]['total_comments'] == 3


def test_calculate_top_authors(silver_df_fixture: DataFrame):
    """
    Testa a função de cálculo de top autores.
    GIVEN: Um DataFrame com dados da camada Silver.
    WHEN: A função calculate_top_authors é chamada.
    THEN: O DataFrame resultante deve agregar corretamente o engajamento por autor.
    """
    # Act
    result_df = calculate_top_authors(silver_df_fixture)
    result_data = {row.author: row for row in result_df.collect()}

    # Assert
    assert len(result_data) == 2

    # user_A
    assert result_data["user_A"]["post_count"] == 2
    assert result_data["user_A"]["likes_total"] == 300  # 100 + 200
    assert result_data["user_A"]["total_engagement"] == 315  # 300 likes + 10 shares + 5 comments

    # user_B
    assert result_data["user_B"]["post_count"] == 1
    assert result_data["user_B"]["likes_total"] == 50
    assert result_data["user_B"]["total_engagement"] == 56  # 50 likes + 5 shares + 1 comment