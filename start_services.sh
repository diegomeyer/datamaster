#!/bin/bash

# Função para checar se um contêiner está rodando
function wait_for_container() {
  container_name=$1
  while [ "$(docker inspect -f '{{.State.Running}}' $container_name)" != "true" ]; do
    echo "Aguardando o contêiner $container_name iniciar..."
    sleep 5
  done
}

# Passo 1: Subir os serviços com Docker Compose
echo "Iniciando todos os serviços com Docker Compose..."
docker compose -f base/docker-compose.yml up -d

# Passo 2: Esperar o Kafka iniciar completamente
echo "Aguardando o Kafka iniciar..."
wait_for_container kafka

# Passo 3: Criar tópicos no Kafka
echo "Criando tópicos no Kafka..."
docker exec -it kafka kafka-topics.sh --create --topic summoners --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1
docker exec -it kafka kafka-topics.sh --create --topic summoner_details --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1
docker exec -it kafka kafka-topics.sh --create --topic matchs --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1
docker exec -it kafka kafka-topics.sh --create --topic matchs_details --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1


echo "Tópico 'summoners' criado com sucesso!"

# Passo 4: Listar todos os tópicos para confirmar
echo "Listando todos os tópicos no Kafka:"
docker exec -it kafka kafka-topics.sh --list --bootstrap-server kafka:9092

echo "Todos os serviços foram iniciados e o tópico foi criado com sucesso."