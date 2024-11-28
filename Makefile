# Variáveis
SEARCH_STRING = INSERT API LOL API KEY
PROJECT_DIR = .

# Regra principal
replace:
	@echo "Substituindo '$(SEARCH_STRING)' por '$(REPLACE_STRING)' no projeto..."
	@find $(PROJECT_DIR) -type f -exec sed -i 's/$(SEARCH_STRING)/$(REPLACE_STRING)/g' {} +
	@echo "Substituição concluída com sucesso."

# Regra para limpar arquivos temporários ou logs, se necessário
clean:
	@echo "Limpando arquivos temporários..."
	@find $(PROJECT_DIR) -name '*.bak' -delete
	@echo "Arquivos temporários removidos."

#Executar testes
tests:
	python -m unittest base.tests

start:
	docker compose rm -svf
	docker compose up