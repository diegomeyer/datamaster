#!/bin/sh
echo "Executando o comando: $@"
sleep 30
exec kafka_exporter
