import time
from fake_api import FakeAPI

if __name__ == "__main__":
    # print(f"Iniciando o processamento de mensagens do tópico {TOPIC_CONSUMER}...")
    fake_api = FakeAPI()
    while True:
     fake_api.generate_posts()
     time.sleep(60)
