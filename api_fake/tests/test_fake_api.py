import pytest
from unittest.mock import MagicMock
from core.fake_api import FakeAPI
from generators.facebook_generator import FacebookDataGenerator
from generators.instagram_generator import InstagramDataGenerator
from generators.x_generator import XDataGenerator

@pytest.fixture
def fake_api():
    """Cria uma instância do FakeAPI com um mock do KafkaClient."""
    kafka_client = MagicMock()
    return FakeAPI(kafka_client)

def test_generate_data(fake_api):
    """Testa se os dados são gerados e enviados corretamente para o Kafka."""
    platform = "facebook"
    fake_api.generate_data(platform, count=1)
    
    # Verifica se o método send_message foi chamado
    fake_api.kafka_client.send_message.assert_called_once()

def test_generate_posts(fake_api):
    """Testa se os posts são gerados para todas as plataformas."""
    fake_api.generate_posts()
    
    # Verifica se o método send_message foi chamado múltiplas vezes
    assert fake_api.kafka_client.send_message.call_count > 0