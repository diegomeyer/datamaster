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
    dag_id='run_gold_batch',
    default_args=default_args,
    description='Processa os dados da camada Silver para Gold diariamente',
    schedule_interval='0 3 * * *',
    start_date=datetime(2024, 11, 22),
    catchup=False
) as dag:

    # Task para executar o script PySpark
    process_silver_to_gold = SparkSubmitOperator(
        task_id='process_silver_to_gold',
        application='/opt/airflow/dags/gold_batch.py',  # Caminho do script PySpark
        name='Process Silver to Gold',
        conn_id='spark_default',  # Conexão Spark configurada no Airflow
        executor_cores=4,
        executor_memory='4g',
        driver_memory='2g',
        num_executors=2,
        verbose=True,
    )

    process_silver_to_gold
