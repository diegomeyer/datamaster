# tests/test_transformations.py
import pytest
from pyspark.sql import SparkSession, Row
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, ArrayType

# Importe as funções que você quer testar
from dags.refactored_silver import transform_facebook
from dags.refactored_gold import calculate_daily_engagement


def test_transform_facebook(spark: SparkSession):
    """
    Testa a função de transformação para dados do Facebook.
    GIVEN: Um DataFrame com o schema de bronze do Facebook.
    WHEN: A função transform_facebook é chamada.
    THEN: O DataFrame resultante deve ter o schema unificado da camada Silver.
    """
    # Arrange: Crie os dados de entrada e o resultado esperado
    source_schema = StructType([
        StructField("user_name", StringType()),
        StructField("post_content", StringType()),
        StructField("created_at", StringType()),
        StructField("likes", IntegerType()),
        StructField("comments", ArrayType(StringType())),  # Simplificado para o teste
        StructField("shares", IntegerType()),
    ])
    source_data = [("user1", "Hello World", "2024-01-01T12:00:00Z", 10, [], 5)]
    source_df = spark.createDataFrame(source_data, source_schema)

    # Act: Chame a função a ser testada
    result_df = transform_facebook(source_df)

    # Assert: Verifique o resultado
    expected_data = [
        Row(author='user1', content='Hello World', post_date=..., likes=10, comments=[], shares=5, source='facebook')
    ]

    result_list = result_df.collect()
    assert len(result_list) == 1
    assert result_list[0]['author'] == 'user1'
    assert result_list[0]['source'] == 'facebook'
    assert result_df.columns == ['author', 'content', 'post_date', 'likes', 'comments', 'shares', 'source']


def test_calculate_daily_engagement(spark: SparkSession):
    """
    Testa a função de cálculo de engajamento diário.
    GIVEN: Um DataFrame com dados da camada Silver.
    WHEN: A função calculate_daily_engagement é chamada.
    THEN: O DataFrame resultante deve conter as métricas de engajamento agregadas corretamente.
    """
    # Arrange
    silver_schema = StructType([
        StructField("source", StringType()),
        StructField("post_date", TimestampType()),
        StructField("likes", IntegerType()),
        StructField("shares", IntegerType()),
        StructField("comments", ArrayType(StringType())),
    ])
    silver_data = [
        ("facebook", datetime(2024, 5, 20, 10), 100, 10, ["c1", "c2"]),
        ("facebook", datetime(2024, 5, 20, 11), 50, 5, ["c3"]),
        ("instagram", datetime(2024, 5, 20, 12), 200, 0, ["c4", "c5", "c6"]),
    ]
    silver_df = spark.createDataFrame(silver_data, silver_schema)

    # Act
    result_df = calculate_daily_engagement(silver_df)

    # Assert
    result_data = sorted(result_df.collect(), key=lambda r: r.source)

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
    assert result_data[1]['total_shares'] == 0
    assert result_data[1]['total_comments'] == 3
