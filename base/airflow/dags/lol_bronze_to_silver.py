from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta

# Argumentos padrão do DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Definição do DAG
with DAG(
    dag_id='lol_bronze_to_silver',
    default_args=default_args,
    description='Processa os dados da camada Bronze para Silver diariamente',
    schedule_interval='0 2 * * *',  # Executa diariamente às 2h da manhã
    start_date=datetime(2023, 11, 22),
    catchup=False
) as dag:

    # Caminhos de entrada e saída
    bronze_path = "hdfs://hadoop-namenode:8020/datalake/bronze/matchs"
    silver_path_participants = "hdfs://hadoop-namenode:8020/datalake/silver/participants"
    silver_path_teams_stats = "hdfs://hadoop-namenode:8020/datalake/silver/teams_stats"
    silver_path_games = "hdfs://hadoop-namenode:8020/datalake/silver/games"
    silver_path_teams_bans = "hdfs://hadoop-namenode:8020/datalake/silver/teams_bans"

    # Task para executar o script PySpark
    process_bronze_to_silver = SparkSubmitOperator(
        task_id='process_bronze_to_silver',
        application='/opt/airflow/dags/bronze_to_silver.py',  # Caminho do script PySpark
        name='Process Bronze to Silver',
        conn_id='spark_default',  # Conexão Spark configurada no Airflow
        application_args=[
            bronze_path,
            silver_path_games,
            silver_path_participants,
            silver_path_teams_stats,
            silver_path_teams_bans
        ],
        executor_cores=4,
        executor_memory='4g',
        driver_memory='2g',
        num_executors=2,
        verbose=True,
    )

    process_bronze_to_silver
