# Dentro do seu arquivo de DAG (ex: silver_dag.py)

from airflow.operators.bash import BashOperator
from airflow.models.dag import DAG
import pendulum

with DAG(
        dag_id='silver_social',
        start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
        catchup=False,
        schedule='*/10 * * * *',
        tags=['silver', 'iceberg'],
) as dag:
    executar_script = BashOperator(
        task_id="silver_unified_batch",
        bash_command="python /opt/airflow/dags/silver_unified_batch.py"
    )

    executar_script