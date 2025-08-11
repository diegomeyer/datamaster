from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='purge_bronze',
    default_args=default_args,
    description='Processa os dados da camada Silver para Gold diariamente',
    schedule='0 3 L * *',
    start_date=datetime(2024, 11, 22),
    catchup=False,
    tags=['bronze', 'purge', 'monthly']
) as dag:
    executar_script = BashOperator(
        task_id="purge_old_bronze_batch",
        bash_command="python /opt/airflow/dags/purge_bronze_batch.py"
    )

    executar_script
