import os
import time

from core.kafka_client import KafkaClient
from core.fake_api import FakeAPI

if __name__ == "__main__":
    kafka_client = KafkaClient(kafka_broker=os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092'))
    fake_api = FakeAPI(kafka_client)

    while True:
     fake_api.generate_posts()
     time.sleep(60)
    # Gerar posts para todas as plataformas