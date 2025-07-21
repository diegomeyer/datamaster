from faker import Faker
import random
from core.data_generator_interface import DataGeneratorInterface

class XDataGenerator(DataGeneratorInterface):
    def __init__(self):
        self.fake = Faker()

    def generate_post(self):
        created_at = self.fake.date_time_between(start_date='-30d', end_date='now')
        return {
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