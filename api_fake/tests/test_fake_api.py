import pytest
from unittest.mock import MagicMock
from core.fake_api import FakeAPI


@pytest.fixture
def fake_api():
    """Cria uma instância do FakeAPI com um mock do KafkaClient."""
    kafka_client = MagicMock()
    return FakeAPI(kafka_client)


def test_generate_data(fake_api):
    """
    Testa a geração de dados para uma plataforma específica.
    GIVEN: Uma instância do FakeAPI com um mock do KafkaClient.
    WHEN: O método generate_data é chamado para a plataforma 'facebook'.
    THEN: O método send_message do cliente Kafka deve ser chamado exatamente uma vez.
    """
    platform = "facebook"
    fake_api.generate_data(platform, count=1)

    # Verifica se o método send_message foi chamado
    fake_api.kafka_client.send_message.assert_called_once()


def test_generate_posts(fake_api):
    """
    Testa a geração de posts para todas as plataformas configuradas.
    GIVEN: Uma instância do FakeAPI com um mock do KafkaClient.
    WHEN: O método generate_posts é chamado.
    THEN: O método send_message do cliente Kafka deve ser chamado múltiplas vezes.
    """
    fake_api.generate_posts()

    # Verifica se o método send_message foi chamado múltiplas vezes
    assert fake_api.kafka_client.send_message.call_count > 0