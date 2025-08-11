
from airflow.operators.bash import BashOperator
from airflow.models.dag import DAG

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

with DAG(
        dag_id='gold_aggregation',
        start_date=datetime(2025, 1, 1),
        catchup=False,
        schedule='0 3 * * *',
        tags=['gold', 'batch', 'diary']
) as dag:
    process_silver_to_gold = BashOperator(
        task_id="process_silver_to_gold",
        bash_command="python /opt/airflow/dags/silver_to_gold_batch.py --processing-date {{ ds }}"
    )

    process_silver_to_gold