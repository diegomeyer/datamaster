from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import requests

import json
import sys

if sys.version_info >= (3, 12, 0):
    import six
    sys.modules['kafka.vendor.six.moves'] = six.moves
from kafka import KafkaProducer
from config import API_KEY

# URL base da API
BASE_URL = 'https://americas.api.riotgames.com'


def send_kafka_message(summoners):
    producer = KafkaProducer(
        bootstrap_servers='kafka:9092',  # Nome do serviço Kafka no docker-compose e a porta padrão
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
    print(summoners)
    try:
        for summoner in summoners['entries']:
            print(summoner)
            message = {
                'timestamp_summoner': datetime.utcnow().isoformat(),
                'summonerId': summoner['summonerId']
            }
            # Enviando a mensagem para o tópico 'test_topic'
            producer.send('summoners', value=message)
            producer.flush()  # Garante que a mensagem é enviada imediatamente
        producer.close()
    except Exception as e:
        print(e)



def get_challegens():
    url = f'https://br1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5'
    headers = {
        'X-Riot-Token': API_KEY
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Erro na requisição: {response.status_code}")
        return None

# Função de exemplo qcue executará uma tarefa genérica
def get_summoners():
    summoners = get_challegens()
    send_kafka_message(summoners)

# Definição da DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'get_summoners_br',
    default_args=default_args,
    description='DAG que captura as informações de ranking br',
    schedule_interval='@hourly',  # Intervalo de execução a cada hora
    start_date=datetime(2024, 1, 1),  # Data inicial da DAG
    catchup=False,  # Desativa a execução retroativa de tarefas anteriores à data de início
) as dag:

    # Tarefa genérica usando o operador Python
    run_generic_task = PythonOperator(
        task_id='send_kafka_message',
        python_callable=get_summoners,
    )

# get_summoners()
