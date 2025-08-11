# Dentro do seu arquivo de DAG (ex: silver_dag.py)
from compact_iceberg_small_files_batch import main

from airflow.operators.python import PythonOperator
from airflow.models.dag import DAG
import pendulum


with DAG(
        dag_id='compact_iceberg_small_files',
        start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
        catchup=False,
        schedule='0 4 * * *',
        tags=['compact', 'small_files'],
) as dag:
    executar_script = PythonOperator(
        task_id="compact_iceberg_small_files_batch",
        python_callable=main,
    )

    executar_script