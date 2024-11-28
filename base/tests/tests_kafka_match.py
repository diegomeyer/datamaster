import unittest
from unittest.mock import patch, MagicMock
from kafka import KafkaConsumer, KafkaProducer
import json
from ..riot.kafka_matchs import Matchs


class TestMatchs(unittest.TestCase):

    def test_get_match_details_success(self):

        match_id = "BR1_3030454409"
        result = Matchs.get_match_details(match_id)

        # Verifica se a API retorna o valor esperado
        self.assertIsNotNone(result)

    def test_get_match_details_failure(self):
        match_id = "BR1_a3030454409"
        result = Matchs.get_match_details(match_id)

        # Verifica se retorna None quando a API falha
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()