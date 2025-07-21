import pytest
from unittest.mock import MagicMock, patch
from core.kafka_client import KafkaClient

@pytest.fixture
def kafka_client():
    """Cria uma instância do KafkaClient com um mock do KafkaProducer."""
    with patch("core.kafka_client.KafkaProducer") as MockKafkaProducer:
        mock_producer = MagicMock()
        MockKafkaProducer.return_value = mock_producer
        kafka_client = KafkaClient(kafka_broker='kafka:9092')
        return kafka_client

def test_send_message(kafka_client):
    """Testa se a mensagem é enviada corretamente para o Kafka."""
    topic = "test-topic"
    message = {"key": "value"}
    
    kafka_client.send_message(topic, message)
    
    # Verifica se o método send foi chamado com os argumentos corretos
    kafka_client.producer.send.assert_called_once_with(topic, value=message)