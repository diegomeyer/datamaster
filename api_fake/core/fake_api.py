import random
from api_fake.core.kafka_client import KafkaClient
from api_fake.generators.facebook_generator import FacebookDataGenerator
from api_fake.generators.instagram_generator import InstagramDataGenerator
from api_fake.generators.x_generator import XDataGenerator

TOPICS = {
    "instagram": "instagram-post",
    "facebook": "facebook-post",
    "x": "x-post",
}

class FakeAPI:
    def __init__(self, kafka_client: KafkaClient):
        self.kafka_client = kafka_client
        self.generators = {
            "facebook": FacebookDataGenerator(),
            "instagram": InstagramDataGenerator(),
            "x": XDataGenerator()
        }

    def generate_data(self, platform: str, count: int = 50):
        if platform not in self.generators:
            raise ValueError("Plataforma inválida. Use 'facebook', 'instagram' ou 'x'.")
        
        generator = self.generators[platform]
        for _ in range(count):
            post = generator.generate_post()
            self.kafka_client.send_message(TOPICS[platform], post)

    def generate_posts(self):
        for platform in self.generators.keys():
            self.generate_data(platform, count=random.randint(20, 50))