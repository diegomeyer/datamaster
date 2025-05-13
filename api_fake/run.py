import json
from datetime import datetime
import time
from kafka import KafkaProducer
from faker import Faker
import random
import json
from datetime import datetime, timedelta

# Configuração do Kafka
KAFKA_BOOTSTRAP_SERVER = 'kafka:9092'
TOPICS = {
    "instagram": "instagram-post",
    "facebook": "facebook-post",
    "x": "x-post",
}

class FakeAPI:
    def __init__(self):
        self.fake = Faker()
        # Inicializar o produtor Kafka
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVER,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    def generate_facebook_post(self):
        created_at = self.fake.date_time_between(start_date='-30d', end_date='now')
        data = {
            "id": self.fake.uuid4(),
            "user_name": self.fake.name(),
            "post_content": self.fake.text(max_nb_chars=280),
            "created_at": created_at.isoformat(),
            "likes": random.randint(0, 5000),
            "shares": random.randint(0, 200),
            "comments": [
                {
                    "user": self.fake.name(),
                    "comment": self.fake.sentence(),
                    "timestamp": self.fake.date_time_between(start_date=created_at, end_date='+10d').isoformat()
                } for _ in range(random.randint(0, 10))
            ]
        }
        return data

    def generate_instagram_post(self):
        created_at = self.fake.date_time_between(start_date='-30d', end_date='now')
        data = {
            "id": self.fake.uuid4(),
            "user_handle": "@" + self.fake.user_name(),
            "caption": self.fake.text(max_nb_chars=150),
            "image_url": self.fake.image_url(),
            "posted_at": created_at.isoformat(),
            "likes": random.randint(0, 10000),
            "hashtags": [f"#{self.fake.word()}" for _ in range(random.randint(1, 5))],
            "comments": [
                {
                    "user": self.fake.name(),
                    "comment": self.fake.sentence(),
                    "timestamp": self.fake.date_time_between(start_date=created_at, end_date='+10d').isoformat()
                } for _ in range(random.randint(0, 10))
            ]
        }
        return data

    def generate_x_post(self):
        created_at = self.fake.date_time_between(start_date='-30d', end_date='now')
        data = {
            "username": self.fake.user_name(),
            "display_name": self.fake.name(),
            "tweet": self.fake.sentence(nb_words=random.randint(5, 20)),
            "likes": random.randint(0, 10000),
            "retweets": random.randint(0, 5000),
            "created_at": created_at.isoformat(),
            "verified": self.fake.boolean(chance_of_getting_true=20),
            "replies": [
                {
                    "username": self.fake.name(),
                    "tweet": self.fake.sentence(),
                    "created_at": self.fake.date_time_between(start_date=created_at, end_date='+10d').isoformat()
                } for _ in range(random.randint(0, 10))
            ]
        }
        return data

    def generate_data(self, platform: str, count: int = 50):
        print(f"Gerando dados - {platform}")
        if platform == "facebook":
            for _ in range(count):
                self.producer.send(TOPICS[platform], value=self.generate_facebook_post())
        elif platform == "instagram":
            for _ in range(count):
                self.producer.send(TOPICS[platform], value=self.generate_instagram_post())
        elif platform == "x":
            for _ in range(count):
                self.producer.send(TOPICS[platform], value=self.generate_x_post())
        else:
            raise ValueError("Plataforma inválida. Use 'facebook' ou 'instagram'.")

    def run(self):
        self.generate_data("facebook", count=random.randint(20, 50))
        self.generate_data("instagram", count=random.randint(20, 50))
        self.generate_data("x", count=random.randint(20, 50))

        # print("== = Facebook ===")
        # print(json.dumps(facebook_data, indent=2))
        #
        # print("\n=== Instagram ===")
        # print(json.dumps(instagram_data, indent=2))

if __name__ == "__main__":
    # print(f"Iniciando o processamento de mensagens do tópico {TOPIC_CONSUMER}...")
    fake_api = FakeAPI()
    while True:
     fake_api.run()
     time.sleep(60)
