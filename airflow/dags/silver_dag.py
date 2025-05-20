from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from datetime import datetime, timedelta

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 5, 11),
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    "silver_social_unify_batch",
    default_args=default_args,
    schedule_interval="*/10 * * * *",  # a cada 10 minutos
    catchup=False,
    description="Executa a transformação Bronze -> Silver unificada a cada 10 minutos",
    tags=['silver', 'batch', '10minutes']
) as dag:

    silver_batch = SparkSubmitOperator(
        task_id="run_silver_batch",
        application="/opt/airflow/dags/silver_unified_batch.py",
        conn_id="spark_default",  # certifique-se que este Spark connection existe no Airflow
        verbose=True,
        conf={"spark.executor.memory": "2g", "spark.driver.memory": "1g"},
        application_args=[],
    )
