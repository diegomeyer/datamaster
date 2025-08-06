import pytest
from pyspark.sql import SparkSession

@pytest.fixture(scope="session")
def spark() -> SparkSession:
    """
    Cria uma SparkSession local para ser usada em toda a suíte de testes.
    A sessão é encerrada automaticamente no final.
    """
    print("--- Criando SparkSession para testes ---")
    session = SparkSession.builder \
        .master("local[*]") \
        .appName("pytest-local-spark") \
        .config("spark.sql.shuffle.partitions", "1") \
        .config("spark.driver.memory", "1g") \
        .getOrCreate()
    yield session
    print("--- Encerrando SparkSession de testes ---")
    session.stop()
