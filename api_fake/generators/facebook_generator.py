from faker import Faker
import random
from api_fake.core.data_generator_interface import DataGeneratorInterface

class FacebookDataGenerator(DataGeneratorInterface):
    def __init__(self):
        self.fake = Faker()

    def generate_post(self):
        created_at = self.fake.date_time_between(start_date='-30d', end_date='now')
        return {
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