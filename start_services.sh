#!/bin/bash
# Variáveis
SEARCH_STRING="CHAVE_API"
REPLACE_STRING="$1"
PROJECT_DIR="."
ESCAPED_REPLACE_STRING=$(printf '%s\n' "$REPLACE_STRING" | sed 's:[\\/&]:\\&:g')

# Verificação do argumento
if [ -z "$REPLACE_STRING" ]; then
    echo "Uso: $0 <REPLACE_STRING>"
    exit 1
fi

# Substituição

# Detectar sistema operacional para definir a flag correta do sed
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS usa `-i ""`
    SED_COMMAND="sed -i \"\""
else
    # Linux usa `-i`
    SED_COMMAND="sed -i"
fi

# Executar a substituição ignorando o próprio script
LC_ALL=C find "$PROJECT_DIR" -type f ! -name "$(basename "$0")" -exec $SED_COMMAND "s/${SEARCH_STRING}/${ESCAPED_REPLACE_STRING}/gI" {} +

echo "Substituição concluída com sucesso."

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
docker compose -f base/docker-compose.yml up --build -d

# Passo 2: Esperar o Kafka iniciar completamente
echo "Aguardando o Kafka iniciar..."
wait_for_container kafka

# Passo 3: Criar tópicos no Kafka
echo "Criando tópicos no Kafka..."
#docker exec -it kafka bash -c "unset KAFKA_OPTS && kafka-topics.sh --delete --topic summoners --bootstrap-server kafka:9092"
#docker exec -it kafka bash -c "unset KAFKA_OPTS && kafka-topics.sh --delete --topic summoner_details --bootstrap-server kafka:9092"
#docker exec -it kafka bash -c "unset KAFKA_OPTS && kafka-topics.sh --delete --topic matchs --bootstrap-server kafka:9092"

docker exec -it kafka bash -c "unset KAFKA_OPTS && kafka-topics.sh --create --topic summoners --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1"
docker exec -it kafka bash -c "unset KAFKA_OPTS && kafka-topics.sh --create --topic summoner_details --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1"
docker exec -it kafka bash -c "unset KAFKA_OPTS && kafka-topics.sh --create --topic matchs --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1"


echo "Tópico 'summoners' criado com sucesso!"

# Passo 4: Listar todos os tópicos para confirmar
echo "Listando todos os tópicos no Kafka:"
docker exec -it kafka bash -c "unset KAFKA_OPTS && kafka-topics.sh --list --bootstrap-server kafka:9092"

wait_for_container hadoop-datanode

docker exec -it hadoop-datanode bash -c "unset HADOOP_OPTS && hdfs dfs -mkdir /datalake"
docker exec -it hadoop-datanode bash -c "unset HADOOP_OPTS && hdfs dfs -chmod -R 777 /datalake"

echo "Todos os serviços foram iniciados e o tópico foi criado com sucesso."
