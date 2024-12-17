from airflow.models import Connection
from airflow import settings

def overwrite_spark_default_connection():
    # Defina os parâmetros da conexão Spark
    conn_id = "spark_default"
    conn_type = "spark"
    conn_host = "spark://spark-master:7077"
    extra = {
        "queue": "default",  # Nome da fila YARN
    }

    # Cria ou atualiza a conexão
    session = settings.Session()

    # Verifica se a conexão já existe
    existing_connection = session.query(Connection).filter(Connection.conn_id == conn_id).first()

    if existing_connection:
        # Atualiza a conexão existente
        existing_connection.conn_type = conn_type
        existing_connection.host = conn_host
        existing_connection.extra = str(extra)
        print(f"Conexão '{conn_id}' atualizada com sucesso.")
    else:
        # Cria uma nova conexão
        new_connection = Connection(
            conn_id=conn_id,
            conn_type=conn_type,
            host=conn_host,
            extra=str(extra),
        )
        session.add(new_connection)
        print(f"Conexão '{conn_id}' criada com sucesso.")

    session.commit()

    # Executa a função para sobrescrever a conexão
overwrite_spark_default_connection()

# Configura a conexão
if __name__ == "__main__":
    overwrite_spark_default_connection()