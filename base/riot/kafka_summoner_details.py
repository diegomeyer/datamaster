import json
import os

import requests
from kafka import KafkaConsumer, KafkaProducer

# Configuração do Kafka
KAFKA_BOOTSTRAP_SERVER = 'kafka:9092'
TOPIC_CONSUMER = 'summoners'
TOPIC_PRODUCER = 'summoner_details'
# LOL_API_URL = 'https://REGION.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}'
API_KEY = os.getenv('API_KEY') # Substitua pela sua chave de API da Riot Games
BASE_URL = 'https://americas.api.riotgames.com'

# Inicializar o consumidor Kafka
consumer = KafkaConsumer(
    TOPIC_CONSUMER,
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
    auto_offset_reset='earliest',
    # group_id='summoner-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Inicializar o produtor Kafka
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


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

def process_messages():
    """Consome mensagens do Kafka, consulta a API e envia novas mensagens para outro tópico."""
    for message in consumer:
        try:
            summoner_id = message.value['summonerId']
            print(f"Recebido invocador: {summoner_id}")

            # Consultar a API para obter detalhes do invocador
            puuid = get_summoner_puuid(summoner_id)
            match_history = get_match_history(puuid)
            if match_history:
                print(f"Partidas recentes: {match_history}")
                for match in match_history:
                    # Enviar os detalhes para o novo tópico
                    producer.send(TOPIC_PRODUCER, value=match)
                print(f"Enviado detalhes do invocador para o tópico '{TOPIC_PRODUCER}'")
        except Exception as e:
            print(f"Erro ao processar mensagem: {e}")

if __name__ == "__main__":
    print(f"Iniciando o processamento de mensagens do tópico {TOPIC_CONSUMER}...")
    process_messages()
