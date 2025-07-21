from faker import Faker
import random
from core.data_generator_interface import DataGeneratorInterface

class InstagramDataGenerator(DataGeneratorInterface):
    def __init__(self):
        self.fake = Faker()

    def generate_post(self):
        created_at = self.fake.date_time_between(start_date='-30d', end_date='now')
        return {
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