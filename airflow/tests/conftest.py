# tests/conftest.py
import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark():
    """Cria uma SparkSession para a suíte de testes."""
    session = SparkSession.builder \
        .master("local[*]") \
        .appName("pytest-spark-session") \
        .getOrCreate()
    yield session
    session.stop()
