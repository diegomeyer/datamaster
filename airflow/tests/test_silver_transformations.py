# airflow/dags/tests/test_silver_transformations.py
import pytest
from pyspark.sql import SparkSession, Row
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType

# Importe as funções que você quer testar
from silver_unified_batch import transform_facebook, transform_x, transform_instagram

def test_transform_facebook(spark: SparkSession):
    """
    Testa a função de transformação para dados do Facebook.
    GIVEN: Um DataFrame com o schema de bronze do Facebook.
    WHEN: A função transform_facebook é chamada.
    THEN: O DataFrame resultante deve ter o schema unificado da camada Silver.
    """
    # Arrange: Crie os dados de entrada
    source_schema = StructType([
        StructField("user_name", StringType()),
        StructField("post_content", StringType()),
        StructField("created_at", StringType()),
        StructField("likes", IntegerType()),
        StructField("comments", ArrayType(StringType())),
        StructField("shares", IntegerType()),
    ])
    source_data = [("user1", "Hello FB", "2024-01-01T12:00:00Z", 10, [], 5)]
    source_df = spark.createDataFrame(source_data, source_schema)

    # Act: Chame a função a ser testada
    result_df = transform_facebook(source_df)
    result_data = result_df.collect()[0]

    # Assert: Verifique o resultado
    assert result_df.columns == ['author', 'content', 'post_date', 'likes', 'comments', 'shares', 'source']
    assert result_data['author'] == 'user1'
    assert result_data['content'] == 'Hello FB'
    assert result_data['source'] == 'facebook'
    assert result_data['shares'] == 5

def test_transform_x(spark: SparkSession):
    """
    Testa a função de transformação para dados do X/Twitter, incluindo a estrutura aninhada.
    GIVEN: Um DataFrame com o schema de bronze do X.
    WHEN: A função transform_x é chamada.
    THEN: O DataFrame resultante deve ter o schema unificado e os comentários devem ser structs.
    """
    # Arrange
    replies_schema = ArrayType(StructType([
        StructField("username", StringType()),
        StructField("tweet", StringType()),
        StructField("created_at", StringType()),
    ]))
    source_schema = StructType([
        StructField("username", StringType()),
        StructField("tweet", StringType()),
        StructField("created_at", StringType()),
        StructField("likes", IntegerType()),
        StructField("replies", replies_schema),
        StructField("retweets", IntegerType()),
    ])
    source_data = [("userX", "Hello X", "2024-01-02T10:00:00Z", 100, [("reply_user", "nice tweet", "2024-01-02T11:00:00Z")], 50)]
    source_df = spark.createDataFrame(source_data, source_schema)

    # Act
    result_df = transform_x(source_df)
    result_data = result_df.collect()[0]

    # Assert
    assert result_df.columns == ['author', 'content', 'post_date', 'likes', 'comments', 'shares', 'source']
    assert result_data['author'] == 'userX'
    assert result_data['source'] == 'twitter'
    assert result_data['shares'] == 50
    # Verifica a estrutura aninhada do comentário
    assert result_data['comments'][0]['user'] == 'reply_user'
    assert result_data['comments'][0]['comment'] == 'nice tweet'

def test_transform_instagram(spark: SparkSession):
    """
    Testa a função de transformação para dados do Instagram.
    GIVEN: Um DataFrame com o schema de bronze do Instagram.
    WHEN: A função transform_instagram é chamada.
    THEN: O DataFrame resultante deve ter o schema unificado, incluindo uma coluna 'shares' nula.
    """
    # Arrange: Crie os dados de entrada
    source_schema = StructType([
        StructField("user_handle", StringType()),
        StructField("caption", StringType()),
        StructField("posted_at", StringType()),
        StructField("likes", IntegerType()),
        StructField("comments", ArrayType(StringType())),
    ])
    source_data = [("insta_user", "My photo", "2024-02-01T20:00:00Z", 150, ["cool!", "nice!"])]
    source_df = spark.createDataFrame(source_data, source_schema)

    # Act: Chame a função a ser testada
    result_df = transform_instagram(source_df)
    result_data = result_df.collect()[0]

    # Assert: Verifique o resultado
    expected_columns = ['author', 'content', 'post_date', 'likes', 'comments', 'shares', 'source']
    assert result_df.columns == expected_columns
    assert result_data['author'] == 'insta_user'
    assert result_data['content'] == 'My photo'
    assert result_data['source'] == 'instagram'
    assert result_data['likes'] == 150
    assert result_data['comments'] == ["cool!", "nice!"]
    # Verifica a criação da coluna 'shares' como nula, que é um caso específico desta transformação
    assert result_data['shares'] is None