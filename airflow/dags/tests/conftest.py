# airflow/dags/tests/conftest.py
import pytest
from pyspark.sql import SparkSession

@pytest.fixture(scope="session")
def spark() -> SparkSession:
    """Cria uma SparkSession local para a suíte de testes."""
    session = SparkSession.builder \
        .master("local[*]") \
        .appName("pytest-local-spark") \
        .getOrCreate()
    yield session
    session.stop()