import json
from datetime import datetime
import time
import requests
from kafka import KafkaConsumer, KafkaProducer

# Configuração do Kafka
KAFKA_BOOTSTRAP_SERVER = 'kafka:9092'
TOPIC_CONSUMER = 'summoners'
TOPIC_PRODUCER = 'summoner_details'
# LOL_API_URL = 'https://REGION.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}'
API_KEY = 'INSERT API LOL API KEY' # Substitua pela sua chave de API da Riot Games
BASE_URL = 'https://americas.api.riotgames.com'



class SummonerDetail:
    def __init__(self):
        # Inicializar o consumidor Kafka
        self.consumer = KafkaConsumer(
            TOPIC_CONSUMER,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
            auto_offset_reset='earliest',
            # group_id='summoner-group',
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

        # Inicializar o produtor Kafka
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    @staticmethod
    def get_summoner_puuid(summoner_id):
        url = f'https://br1.api.riotgames.com/lol/summoner/v4/summoners/{summoner_id}'
        headers = {
            'X-Riot-Token': API_KEY
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()["puuid"]
        else:
            print(f"Erro na requisição: {response.status_code}")
            return None

    # Função para obter as partidas recentes do jogador
    @staticmethod
    def get_match_history(puuid, count=5):
        url = f'{BASE_URL}/lol/match/v5/matches/by-puuid/{puuid}/ids?start=0&count={count}'
        headers = {
            'X-Riot-Token': API_KEY
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Erro na requisição: {response.status_code}")
            return None

    def process_messages(self):
        """Consome mensagens do Kafka, consulta a API e envia novas mensagens para outro tópico."""
        for message in self.consumer:
            try:
                dict_message = message.value
                summoner_id = dict_message['summonerId']
                print(f"Recebido invocador: {summoner_id}")

                # Consultar a API para obter detalhes do invocador
                puuid = self.get_summoner_puuid(summoner_id)
                match_history = self.get_match_history(puuid)
                if match_history:
                    print(f"Partidas recentes: {match_history}")
                    for match in match_history:
                        # Enviar os detalhes para o novo tópico
                        dict_match = dict_message.copy()
                        dict_match.update({"timestamp_summoner_details":datetime.utcnow().isoformat(), "match_id": match})
                        self.producer.send(TOPIC_PRODUCER, value=dict_match)
                    print(f"Enviado detalhes do invocador para o tópico '{TOPIC_PRODUCER}'")
            except Exception as e:
                print(f"Erro ao processar mensagem: {e}")
            print("Esperando o timer")
            time.sleep(2)

if __name__ == "__main__":
    print(f"Iniciando o processamento de mensagens do tópico {TOPIC_CONSUMER}...")
    summoner_detail = SummonerDetail()
    summoner_detail.process_messages()
