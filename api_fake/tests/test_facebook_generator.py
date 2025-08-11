import pytest
from unittest.mock import MagicMock, patch
from core.kafka_client import KafkaClient


@pytest.fixture
def kafka_client():
    """Cria uma instância do KafkaClient com um mock do KafkaProducer para os testes."""
    with patch("core.kafka_client.KafkaProducer") as MockKafkaProducer:
        mock_producer = MagicMock()
        MockKafkaProducer.return_value = mock_producer
        client = KafkaClient(kafka_broker='kafka:9092')
        # Adicionei o mock como um atributo para facilitar o acesso nos testes
        client.producer = mock_producer
        return client


def test_send_message(kafka_client):
    """
    Testa o envio de uma mensagem para o Kafka.
    GIVEN: Uma instância do KafkaClient com um produtor mockado.
    WHEN: O método send_message é chamado com um tópico e uma mensagem.
    THEN: O método 'send' do produtor deve ser chamado exatamente uma vez com os argumentos corretos.
    """
    # Arrange
    topic = "test-topic"
    message = {"key": "value"}

    # Act
    kafka_client.send_message(topic, message)

    # Assert: Verifica se o método send foi chamado com os argumentos corretos
    kafka_client.producer.send.assert_called_once_with(topic, value=message)
