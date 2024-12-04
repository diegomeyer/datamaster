# Variáveis
SEARCH_STRING = CHAVE_API
PROJECT_DIR = .

# Regra principal
replace:
	@echo "Substituindo '$(SEARCH_STRING)' por '$(REPLACE_STRING)' no projeto..."
	@find $(PROJECT_DIR) -type f -exec sed -i 's/$(SEARCH_STRING)/$(REPLACE_STRING)/g' {} +
	@echo "Substituição concluída com sucesso."

#Executar testes
tests:
	python -m unittest base.tests

start:
	docker compose rm -svf
	docker compose up