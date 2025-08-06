from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, from_json, current_timestamp, date_format
from pyspark.sql.types import StructType
import os


class KafkaToBronzeStreamer:
    """
    Encapsula a lógica para streaming de dados de um tópico Kafka para uma tabela Bronze Iceberg.
    """

    def __init__(self, spark: SparkSession, source_config: dict):
        self.spark = spark
        self.config = source_config
        self.kafka_bootstrap_servers = os.getenv("KAFKA_BOOTSTRAP_SERVERS")
        if not self.kafka_bootstrap_servers:
            raise ValueError("A variável de ambiente KAFKA_BOOTSTRAP_SERVERS não está definida.")

    def _read_stream(self) -> DataFrame:
        """Lê o stream de dados do tópico Kafka configurado."""
        print(f"Lendo do tópico Kafka: {self.config['kafka_topic']}")
        return self.spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.kafka_bootstrap_servers) \
            .option("subscribe", self.config['kafka_topic']) \
            .option("startingOffsets", "earliest") \
            .option("failOnDataLoss", "false") \
            .load()

    def _transform(self, df_raw: DataFrame) -> DataFrame:
        """Analisa o payload JSON e adiciona metadados de ingestão."""
        print("Aplicando transformações: parsing de JSON e adição de timestamps.")
        df_parsed = df_raw.selectExpr("CAST(value AS STRING) as json") \
            .withColumn("data", from_json(col("json"), self.config['schema'])) \
            .select("data.*")

        return df_parsed.withColumn("event_time", current_timestamp()) \
            .withColumn("ingestion_date", date_format(col("event_time"), "yyyy-MM-dd"))

    def _write_stream(self, df_transformed: DataFrame):
        """Escreve o DataFrame transformado na tabela Iceberg de destino."""
        print(f"Escrevendo stream para a tabela Iceberg: {self.config['table_name']}")
        print(f"Usando local de checkpoint: {self.config['checkpoint_location']}")
        return df_transformed.writeStream \
            .format("iceberg") \
            .partitionBy("ingestion_date") \
            .outputMode("append") \
            .trigger(processingTime="10 minutes") \
            .option("checkpointLocation", self.config['checkpoint_location']) \
            .toTable(self.config['table_name'])

    def run(self):
        """Executa o job de streaming de ponta a ponta."""
        raw_df = self._read_stream()
        transformed_df = self._transform(raw_df)
        query = self._write_stream(transformed_df)
        query.awaitTermination()