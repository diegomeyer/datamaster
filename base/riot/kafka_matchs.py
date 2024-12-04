import json
from datetime import datetime
import time

import requests
from kafka import KafkaConsumer, KafkaProducer

# Configuração do Kafka
KAFKA_BOOTSTRAP_SERVER = 'kafka:9092'
TOPIC_CONSUMER = 'summoner_details'
TOPIC_PRODUCER = 'matchs'
# LOL_API_URL = 'https://REGION.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}'
API_KEY = 'CHAVE_API'  # Substitua pela sua chave de API da Riot Games
BASE_URL = 'https://americas.api.riotgames.com'


class Matchs:
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


    # Função para obter detalhes de uma partida
    @staticmethod
    def get_match_details(match_id):
        url = f'https://americas.api.riotgames.com/lol/match/v5/matches/{match_id}'
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
        try:
            for message in self.consumer:
                dict_message = message.value
                match_id = dict_message["match_id"]
                print(f"Match ID: {match_id}")

                match_details = self.get_match_details(match_id)
                if match_details:
                    dict_detail = dict_message.copy()
                    dict_detail.update({"timestamp_match": datetime.utcnow().isoformat(), "match_details": match_details})
                    self.producer.send(TOPIC_PRODUCER, value=dict_detail)
                    print(f"Enviado detalhes do da partida para o topico '{TOPIC_PRODUCER}'")
                print("Esperando o timer")
                time.sleep(0.8)
        except Exception as e:
            print(f"Erro ao processar mensagem: {e}")



if __name__ == "__main__":
    print(f"Iniciando o processamento de mensagens do tópico {TOPIC_CONSUMER}...")
    matchs = Matchs()
    matchs.process_messages()