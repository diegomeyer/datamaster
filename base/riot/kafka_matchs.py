import json
import os

import requests
from kafka import KafkaConsumer, KafkaProducer

# Configuração do Kafka
KAFKA_BOOTSTRAP_SERVER = 'kafka:9092'
TOPIC_CONSUMER = 'summoner_details'
TOPIC_PRODUCER = 'matchs'
# LOL_API_URL = 'https://REGION.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}'
API_KEY = os.getenv("API_KEY")  # Substitua pela sua chave de API da Riot Games
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


# Função para obter detalhes de uma partida
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

def process_messages():
    """Consome mensagens do Kafka, consulta a API e envia novas mensagens para outro tópico."""
    try:
        for message in consumer:
            match_id = message.value
            print(f"Match ID: {match_id}")

            match_details = get_match_details(match_id)
            if match_details:
                producer.send(TOPIC_PRODUCER, value=match_details)
                print(f"Enviado detalhes do da partida para o topico '{TOPIC_PRODUCER}'")
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")

if __name__ == "__main__":
    print(f"Iniciando o processamento de mensagens do tópico {TOPIC_CONSUMER}...")
    process_messages()