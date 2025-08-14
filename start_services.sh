#!/bin/bash
# Variáveis
#SEARCH_STRING="CHAVE_API"
#REPLACE_STRING="$1"
#PROJECT_DIR="."
#ESCAPED_REPLACE_STRING=$(printf '%s\n' "$REPLACE_STRING" | sed 's:[\\/&]:\\&:g')
#
## Verificação do argumento
#if [ -z "$REPLACE_STRING" ]; then
#    echo "Uso: $0 <REPLACE_STRING>"
#    exit 1
#fi
#
## Substituição
#
## Detectar sistema operacional para definir a flag correta do sed
#if [[ "$OSTYPE" == "darwin"* ]]; then
#    # macOS usa `-i ""`
#    SED_COMMAND="sed -i \"\""
#else
#    # Linux usa `-i`
#    SED_COMMAND="sed -i"
#fi
#
## Executar a substituição ignorando o próprio script
#LC_ALL=C find "$PROJECT_DIR" -type f ! -name "$(basename "$0")" -exec $SED_COMMAND "s/${SEARCH_STRING}/${ESCAPED_REPLACE_STRING}/gI" {} +
#
#echo "Substituição concluída com sucesso."
#
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
docker compose -f docker-compose.yml up --build -d

# Passo 2: Esperar o Kafka iniciar completamente
echo "Aguardando o Kafka iniciar..."
wait_for_container kafka

# Passo 3: Criar tópicos no Kafka
echo "Criando tópicos no Kafka..."
docker exec -it kafka bash -c "unset KAFKA_OPTS && kafka-topics.sh --create --topic instagram-post --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1"
docker exec -it kafka bash -c "unset KAFKA_OPTS && kafka-topics.sh --create --topic facebook-post --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1"
docker exec -it kafka bash -c "unset KAFKA_OPTS && kafka-topics.sh --create --topic x-post --bootstrap-server kafka:9092 --partitions 1 --replication-factor 1"


echo "Tópicos criado com sucesso!"

# Passo 4: Listar todos os tópicos para confirmar
echo "Listando todos os tópicos no Kafka:"
docker exec -it kafka bash -c "unset KAFKA_OPTS && kafka-topics.sh --list --bootstrap-server kafka:9092"

