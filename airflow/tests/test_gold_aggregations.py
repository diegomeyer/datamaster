# airflow/dags/tests/test_gold_aggregations.py
import pytest
from datetime import datetime
from pyspark.sql import SparkSession, Row, DataFrame
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, TimestampType, ArrayType, LongType

# Importe as funções que você quer testar
from silver_to_gold_batch import (
    calculate_daily_engagement,
    calculate_top_authors,
    calculate_hourly_distribution
)


@pytest.fixture(scope="session")
def spark():
    """Creates a SparkSession for the test session."""
    session = (
        SparkSession.builder.master("local[2]")
        .appName("pytest-pyspark-testing")
        .getOrCreate()
    )
    yield session
    session.stop()

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

@pytest.fixture(scope="module")
def silver_df_basic_distribution(spark: SparkSession) -> DataFrame:
    """Cria um DataFrame de exemplo simulando a tabela Silver para os testes."""
    schema = StructType([
        StructField("source", StringType(), True),
        StructField("post_date", TimestampType(), True),
    ])
    data = [
        ("Facebook", datetime(2023, 1, 1, 10, 30, 0)),
        ("Facebook", datetime(2023, 1, 1, 10, 55, 0)),  # Same hour
        ("Twitter", datetime(2023, 1, 1, 15, 0, 0)),
        ("Twitter", datetime(2023, 1, 2, 15, 10, 0)),  # Same hour, different day
        ("Instagram", datetime(2023, 1, 3, 22, 0, 0)),
    ]
    return spark.createDataFrame(data, schema)

@pytest.fixture(scope="module")
def silver_df_empty(spark: SparkSession) -> DataFrame:
    """Cria um DataFrame de exemplo simulando a tabela Silver para os testes."""
    schema = StructType([
        StructField("source", StringType(), True),
        StructField("post_date", TimestampType(), True),
    ])
    return spark.createDataFrame([], schema)

@pytest.fixture(scope="module")
def silver_df_null_values(spark: SparkSession) -> DataFrame:
    """Cria um DataFrame de exemplo simulando a tabela Silver para os testes."""
    schema = StructType([
        StructField("source", StringType(), True),
        StructField("post_date", TimestampType(), True),
    ])
    data = [
        ("Facebook", datetime(2023, 1, 1, 8, 0, 0)),
        (None, datetime(2023, 1, 1, 8, 15, 0)),  # Null source
        ("Twitter", None),  # Null date
    ]
    return spark.createDataFrame(data, schema)

@pytest.fixture(scope="module")
def silver_df_single_source_and_hour(spark: SparkSession) -> DataFrame:
    """Cria um DataFrame de exemplo simulando a tabela Silver para os testes."""
    # Arrange
    schema = StructType([
        StructField("source", StringType(), True),
        StructField("post_date", TimestampType(), True),
    ])
    data = [
        ("x", datetime(2023, 5, 5, 9, 0, 0)),
        ("x", datetime(2023, 5, 6, 9, 10, 0)),
        ("x", datetime(2023, 5, 7, 9, 20, 0)),
    ]
    return spark.createDataFrame(data, schema)


def test_calculate_daily_engagement(silver_df_fixture: DataFrame):
    """
    Testa a função de cálculo de engajamento diário.
    GIVEN: Um DataFrame com dados da camada Silver.
    WHEN: A função calculate_daily_engagement é chamada.
    THEN: O DataFrame resultante deve conter as métricas de engajamento agregadas corretamente por fonte.
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
    assert result_data[1]['total_shares'] == 0
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


def test_basic_distribution(silver_df_basic_distribution: DataFrame):
    """
    Testa a funcionalidade básica de distribuição horária com múltiplas fontes e datas.
    GIVEN: Um DataFrame com posts de diferentes fontes em diferentes horas e dias.
    WHEN: A função calculate_hourly_distribution é chamada.
    THEN: O resultado deve ser um DataFrame agrupado por fonte e hora com a contagem correta de posts.
    """
    actual_df = calculate_hourly_distribution(silver_df_basic_distribution)

    # Assert: Check the results
    expected_data = [
        Row(source="Facebook", hour=10, total_posts=2),
        Row(source="Instagram", hour=22, total_posts=1),
        Row(source="Twitter", hour=15, total_posts=2),
    ]

    # Collect and sort for reliable comparison
    actual_results = sorted(actual_df.collect(), key=lambda r: r.source)

    assert actual_results == expected_data
    assert actual_df.count() == 3
    # Check schema
    assert "source" in actual_df.columns
    assert "hour" in actual_df.columns
    assert "total_posts" in actual_df.columns

def test_empty_dataframe(silver_df_empty: DataFrame):
    """
    Testa o comportamento da função com um DataFrame de entrada vazio.
    GIVEN: Um DataFrame vazio com o schema esperado.
    WHEN: A função calculate_hourly_distribution é chamada.
    THEN: O resultado deve ser um DataFrame vazio com o schema de saída correto.
    """
    # Act: Call the function
    actual_df = calculate_hourly_distribution(silver_df_empty)

    # Assert: The result should be an empty DataFrame with the expected output schema
    assert actual_df.count() == 0
    expected_schema = StructType([
        StructField("source", StringType(), True),
        StructField("hour", IntegerType(), True),
        StructField("total_posts", LongType(), False),  # count is not nullable
    ])
    assert str(actual_df.schema) == str(expected_schema)

def test_with_null_values(silver_df_null_values: DataFrame):
    """
    Testa como a função lida com valores nulos nas colunas 'source' e 'post_date'.
    GIVEN: Um DataFrame contendo valores nulos nas colunas de agrupamento.
    WHEN: A função calculate_hourly_distribution é chamada.
    THEN: Os valores nulos devem ser agrupados corretamente, sem causar erros.
    """
    # Act: Call the function
    actual_df = calculate_hourly_distribution(silver_df_null_values)

    # Assert: Check the results. Nulls are grouped together.
    # Default sorting places nulls first.
    expected_data = [
        Row(source=None, hour=8, total_posts=1),
        Row(source="Facebook", hour=8, total_posts=1),
        Row(source="Twitter", hour=None, total_posts=1),
    ]

    actual_results = actual_df.collect()

    assert actual_results == expected_data
    assert actual_df.count() == 3

def test_single_source_and_hour(silver_df_single_source_and_hour: DataFrame):
    """
    Testa o cálculo da distribuição horária com dados de uma única fonte e hora.
    GIVEN: Um DataFrame com múltiplas entradas para a mesma fonte e hora.
    WHEN: A função calculate_hourly_distribution é chamada.
    THEN: O DataFrame resultante deve conter uma única linha com a contagem correta de posts.
    """
    # Act
    actual_df = calculate_hourly_distribution(silver_df_single_source_and_hour)

    # Assert
    expected_data = [
        Row(source="x", hour=9, total_posts=3)
    ]
    actual_results = actual_df.collect()

    assert actual_results == expected_data
    assert actual_df.count() == 1