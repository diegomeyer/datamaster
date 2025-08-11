import pytest
import json
from pyspark.sql import SparkSession, Row
from pyspark.sql.types import StructType, StringType



# Importe as classes e configurações que você vai testar
from common.streaming_job import KafkaToBronzeStreamer
from configs.source_definitions import SOURCE_CONFIGS

# Pega uma configuração de exemplo para usar nos testes
TEST_SOURCE_CONFIG = SOURCE_CONFIGS["facebook"]


def test_transform_logic(spark: SparkSession):
    """
    Testa a lógica de transformação do streamer.
    GIVEN: Um DataFrame com dados brutos do Kafka (coluna 'value' como JSON string).
    WHEN: O método _transform é chamado.
    THEN: O DataFrame resultante deve ter o schema correto, com o JSON parseado
          e as colunas de metadados (`event_time`, `ingestion_date`) adicionadas.
    """
    # Arrange: Crie os dados de entrada
    streamer = KafkaToBronzeStreamer(spark, TEST_SOURCE_CONFIG)

    raw_kafka_data = [
        Row(value=json.dumps({
            "id": "post123",
            "user_name": "test_user",
            "post_content": "Hello Spark!",
            "created_at": "2024-01-01T12:00:00Z",
            "likes": 150,
            "shares": 20,
            "comments": []
        }))
    ]

    # Crie um DataFrame com o schema que o Kafka fornece
    kafka_schema = StructType().add("value", StringType())
    input_df = spark.createDataFrame(raw_kafka_data, schema=kafka_schema)

    # Act: Chame o método que está sendo testado
    transformed_df = streamer._transform(input_df)
    result_data = transformed_df.collect()[0]

    # Assert: Verifique se o resultado está correto
    assert "user_name" in transformed_df.columns
    assert "ingestion_date" in transformed_df.columns
    assert "event_time" in transformed_df.columns

    assert result_data["user_name"] == "test_user"
    assert result_data["likes"] == 150
    assert result_data["ingestion_date"] is not None
    assert result_data["event_time"] is not None


def test_run_orchestration(spark: SparkSession, mocker):
    """
    Testa a orquestração do método run() usando mocks.
    GIVEN: Uma instância do KafkaToBronzeStreamer.
    WHEN: O método run() é chamado.
    THEN: Os métodos internos _read_stream, _transform e _write_stream devem
          ser chamados exatamente uma vez, na sequência correta.
    """
    # Arrange: Crie a instância e os mocks
    streamer = KafkaToBronzeStreamer(spark, TEST_SOURCE_CONFIG)

    # Crie um mock para cada método interno. Isso impede que eles executem
    # sua lógica real (conectar ao Kafka, etc.)
    mock_read = mocker.patch.object(streamer, '_read_stream')
    mock_transform = mocker.patch.object(streamer, '_transform')
    mock_write = mocker.patch.object(streamer, '_write_stream')

    # O método _write_stream retorna um objeto de query, que também precisa ser mockado
    # para evitar que o teste fique travado em `awaitTermination`.
    mock_query = mocker.MagicMock()
    mock_write.return_value = mock_query

    # Act: Chame o método principal
    streamer.run()

    # Assert: Verifique se os mocks foram chamados como esperado
    mock_read.assert_called_once()

    # Verifica se _transform foi chamado com o resultado de _read_stream
    mock_transform.assert_called_once_with(mock_read.return_value)

    # Verifica se _write_stream foi chamado com o resultado de _transform
    mock_write.assert_called_once_with(mock_transform.return_value)

    # Verifica se a espera pela query foi chamada
    mock_query.awaitTermination.assert_called_once()