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
    dag_id='lol_silver_to_gold',
    default_args=default_args,
    description='Processa os dados da camada Bronze para Silver diariamente',
    schedule_interval='0 3 * * *',  # Executa diariamente às 2h da manhã
    start_date=datetime(2024, 11, 22),
    catchup=False
) as dag:

    # Caminhos de entrada e saída
    silver_path_participants = "hdfs://hadoop-namenode:8020/datalake/silver/participants"
    silver_path_teams_stats = "hdfs://hadoop-namenode:8020/datalake/silver/teams_stats"
    silver_path_games = "hdfs://hadoop-namenode:8020/datalake/silver/games"
    silver_path_teams_bans = "hdfs://hadoop-namenode:8020/datalake/silver/teams_bans"
    gold_path_match_summary = "hdfs://hadoop-namenode:8020/datalake/gold/match_summary"
    gold_path_player_performance = "hdfs://hadoop-namenode:8020/datalake/gold/player_performance"
    gold_path_team_performance = "hdfs://hadoop-namenode:8020/datalake/gold/team_performance"

    # Task para executar o script PySpark
    process_silver_to_gold = SparkSubmitOperator(
        task_id='process_silver_to_gold',
        application='/opt/airflow/dags/lol_silver_to_gold.py',  # Caminho do script PySpark
        name='Process Silver to Gold',
        conn_id='spark_default',  # Conexão Spark configurada no Airflow
        application_args=[
            silver_path_games,
            silver_path_participants,
            silver_path_teams_stats,
            silver_path_teams_bans,
            gold_path_match_summary,
            gold_path_player_performance,
            gold_path_team_performance

        ],
        executor_cores=4,
        executor_memory='4g',
        driver_memory='2g',
        num_executors=2,
        verbose=True,
    )

    process_silver_to_gold
