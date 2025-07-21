<p align="center" width="100%">
    <img width="33%" src="https://github.com/diegomeyer/datamaster/blob/develop/dm.jpg">
</p>

-----

## 🎯 **Objetivo do Projeto**

Este projeto tem como objetivo desenvolver uma solução completa de engenharia de dados para consumir informações de APIs de redes sociais em tempo real. Para simular esse fluxo, utilizamos a biblioteca `Faker`.

O pipeline de dados foi projetado para processar e armazenar as informações em um **Data Lake** estruturado em camadas (`bronze`, `silver` e `gold`). Além disso, a solução implementa recursos de **monitoramento** e **observabilidade** para garantir a rastreabilidade do fluxo, a detecção de falhas e a identificação de gargalos de desempenho.

-----

## 🚀 **Início Rápido**

### **Configuração do Ambiente**

Para iniciar todos os serviços necessários, execute o comando abaixo no seu terminal. Ele garantirá que toda a infraestrutura da solução esteja operacional.

```bash
./start_services.sh
```

### **Testes**

Para garantir a qualidade e o correto funcionamento dos componentes, o projeto conta com testes unitários. Para executar os testes do componente `api_fake`, que simula a geração de dados.

É crucial configurar a variável de ambiente `PYTHONPATH` para que o Python consiga localizar os módulos do projeto corretamente, especialmente porque os testes utilizam importações absolutas a partir da raiz do projeto.

1.  **Navegue até o diretório raiz do projeto** no seu terminal.

2.  **Exporte a variável `PYTHONPATH`** para apontar para o diretório api_fake `export PYTHONPATH=$(pwd)/api_fake`. Este comando adiciona a pasta raiz do projeto ao caminho de busca de módulos do Python.

3.  **Execute os testes** utilizando o `pytest`. Com isso execute  `pytest api_fake/test`

    



```bash
./start_services.sh
```
-----

## 🏗️ **Arquitetura da Solução**

O pipeline de dados foi projetado com as seguintes etapas:

1.  **Extração em Tempo Real**:

      * Dados de redes sociais são simulados com a biblioteca `Faker`.
      * As informações geradas são enviadas para tópicos dedicados no **Apache Kafka**.

2.  **Processamento e Ingestão (Bronze)**:

      * O **PySpark** consome os dados dos tópicos do Kafka em tempo real.
      * Os dados brutos são gravados na camada `bronze` do Data Lake em formato Parquet, garantindo a integridade original da informação.

3.  **Transformação e Limpeza (Silver)**:

      * Os dados da camada `bronze` são processados, limpos e normalizados.
      * O resultado é armazenado na camada `silver`, pronta para análises mais estruturadas.

4.  **Agregação e Análise (Gold)**:

      * A camada `gold` é criada a partir da camada `silver`, contendo agregações e métricas de negócio (KPIs) prontas para consumo por ferramentas de BI e análise de dados.

5.  **Monitoramento Contínuo**:

      * Métricas de performance de todo o pipeline são coletadas pelo **Prometheus** e visualizadas em dashboards interativos no **Grafana**.

### **Visão Geral da Arquitetura**

### **Tecnologias Utilizadas**

| Tecnologia | Função na Arquitetura |
| :--- | :--- |
| **Docker Compose** | Orquestração e gerenciamento dos contêineres da solução. |
| **Apache Kafka** | Sistema de mensageria para ingestão de dados em tempo real. |
| **PySpark** | Ferramenta para processamento distribuído de grandes volumes de dados. |
| **HDFS** | Sistema de arquivos distribuído, utilizado como Data Lake. |
| **Airflow** | Orquestrador para agendamento e automação dos fluxos de trabalho (DAGs). |
| **Prometheus** | Sistema de monitoramento e coleta de métricas. |
| **Grafana** | Plataforma para visualização e análise das métricas coletadas. |
| **Jupyter** | Ambiente interativo para exploração e análise de dados. |
| **Kafka Exporter**| Ferramenta para exportar métricas do Kafka para o Prometheus. |

-----

## 🔧 **Detalhes da Implementação**

#### **1. Extração de Dados**

O script `api_fake/main.py` é responsável por gerar dados sintéticos que simulam posts de redes sociais e publicá-los nos tópicos `instagram-post`, `facebook-post` e `x-post` do Kafka.

#### **2. Processamento e Armazenamento**

  * **Kafka para Bronze**: O script `kafka_to_bronze.py` consome as mensagens do Kafka em tempo real e armazena os dados brutos na camada `bronze`. Este processo utiliza checkpoints para garantir a tolerância a falhas.
  * **Bronze para Silver**: A DAG `silver_unified_batch.py` no Airflow orquestra a transformação dos dados brutos, unificando e estruturando as informações mais relevantes na camada `silver`.
  * **Silver para Gold**: A DAG `gold_batch.py` consome os dados da camada `silver` e executa agregações para gerar KPIs, como o total de interações por usuário, armazenando o resultado na camada `gold`.

#### **3. Estrutura do Data Lake**

  * **Camada Bronze**: Armazena os dados brutos, exatamente como foram recebidos das fontes, em formato Parquet.
  * **Camada Silver**: Contém dados limpos, normalizados e enriquecidos, prontos para análises mais complexas.
  * **Camada Gold**: Apresenta dados agregados e métricas de negócio (KPIs), otimizados para consumo final.

#### **4. Conformidade com a LGPD**

Os dados utilizados neste projeto são sintéticos e não contêm informações pessoais sensíveis. Em um cenário com dados reais, técnicas de anonimização como **generalização, supressão, k-anonimidade e tokenização** poderiam ser aplicadas para garantir a conformidade com a Lei Geral de Proteção de Dados (LGPD).

-----

## ✨ **Melhorias e Próximos Passos**

Para evoluir a solução, as seguintes melhorias são sugeridas:

1.  **Escalabilidade**:

      * Implementar particionamento nos tópicos do Kafka e otimizar o paralelismo no PySpark para suportar um volume maior de dados.
      * Expandir o cluster HDFS com múltiplos nós para aumentar a capacidade de armazenamento.

2.  **Observabilidade Avançada**:

      * Integrar o **OpenTelemetry** para adicionar rastreamento distribuído, permitindo um monitoramento detalhado da latência em cada componente do pipeline.

3.  **Governança de Dados**:

      * Implementar políticas de retenção e expurgo automático de dados em cada camada do Data Lake.
      * Adotar um catálogo de dados para documentar e facilitar a descoberta dos ativos de dados.

4.  **Segurança**:

      * Habilitar mecanismos de autenticação e autorização no Kafka.
      * Criptografar dados sensíveis em repouso no Data Lake.
      * Utilizar um "cofre" de segredos (como o HashiCorp Vault) para gerenciar chaves de API e credenciais.

-----

### **Considerações Finais**

A solução desenvolvida apresenta um pipeline de dados robusto e moderno para ingestão, processamento e armazenamento de dados em tempo real. A arquitetura, baseada em tecnologias consolidadas no mercado, garante escalabilidade, flexibilidade e observabilidade. As melhorias sugeridas podem tornar a plataforma ainda mais eficiente e confiável, assegurando uma governança de dados sólida e capacidade para lidar com desafios de Big Data cada vez maiores.
