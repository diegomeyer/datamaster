# Dentro do seu arquivo de DAG (ex: silver_dag.py)

from airflow.operators.bash import BashOperator
from airflow.models.dag import DAG
import pendulum

with DAG(
        dag_id='batch_silver_social',
        start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
        catchup=False,
        schedule=None,
        tags=['silver', 'iceberg'],
) as dag:
    executar_script = BashOperator(
        task_id="silver_unified_batch",
        bash_command="python /opt/airflow/dags/silver_unified_batch.py --processing-date {{ds}}"
    )

    executar_script