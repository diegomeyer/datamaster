from kafka import KafkaProducer
import json

class KafkaClient:
    """Classe responsável por gerenciar a comunicação com o Kafka."""
    
    def __init__(self, kafka_broker='kafka:9092'):
        self.producer = KafkaProducer(
            bootstrap_servers=kafka_broker,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def send_message(self, topic: str, message: dict):
        """Envia uma mensagem para o tópico especificado."""
        self.producer.send(topic, value=message)