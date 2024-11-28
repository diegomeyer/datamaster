import unittest
from unittest.mock import patch, MagicMock
from ..riot.kafka_summoner_details import SummonerDetail

class TestSummonerFunctions(unittest.TestCase):

    def test_get_summoner_puuid_success(self):
        # Chama a função com um summoner_id de teste
        summoner_id = "yXoeuPWPrbI7y0VMElnd0hkh8gzfJu0VI-Vc4O8fue-5fSnij0hP22Q5pQ"
        result = SummonerDetail.get_summoner_puuid(summoner_id)

        # Verifica se o resultado é o esperado
        self.assertEqual(result, "9FaoTGFLOeF3FVIEEMbyOj5S5sZ7paudIQpwWhl1ErMoJacaVpakLcZ_xKVXhAiP_5TOzwMlw9GHrw")

    def test_get_summoner_puuid_failure(self):
        # Chama a função com um summoner_id inválido
        summoner_id = "invalid_id"
        result = SummonerDetail.get_summoner_puuid(summoner_id)

        # Verifica se a função retorna None em caso de falha
        self.assertIsNone(result)

    def test_get_match_history_success(self):
        # Configura o mock para simular uma resposta bem-sucedida
        # Chama a função com um PUUID de teste
        puuid = "9FaoTGFLOeF3FVIEEMbyOj5S5sZ7paudIQpwWhl1ErMoJacaVpakLcZ_xKVXhAiP_5TOzwMlw9GHrw"
        count = 3
        result = SummonerDetail.get_match_history(puuid, count)

        # Verifica se o resultado é o esperado
        self.assertEqual(len(result), 3)

    def test_get_match_history_failure(self):
        # Chama a função com um PUUID inválido
        puuid = "invalid_puuid"
        result = SummonerDetail.get_match_history(puuid)

        # Verifica se a função retorna None em caso de falha
        self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()
