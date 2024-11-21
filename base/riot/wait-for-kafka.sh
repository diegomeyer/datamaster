#!/bin/bash
host="$1"
shift
cmd="$@"

# Aguardar até que o serviço Kafka esteja disponível
until nc -z "$host" 9092; do
  echo "Aguardando Kafka em $host:9092..."
  sleep 5
done

echo "Kafka está disponível - executando comando"
echo $cmd
exec $cmd
