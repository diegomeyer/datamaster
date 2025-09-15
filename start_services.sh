#!/bin/bash
# Passo 1: Subir os serviços com Docker Compose
echo "Iniciando todos os serviços com Docker Compose..."
docker compose -f docker-compose.yml up --build -d

