import argparse
import sys
from common.spark_utils import get_spark_session
from common.streaming_job import KafkaToBronzeStreamer
from configs.source_definitions import SOURCE_CONFIGS


def main():
    """
    Ponto de entrada principal para executar jobs de ingestão Kafka para Bronze.
    """
    parser = argparse.ArgumentParser(
        description="Executa um job de streaming Kafka para Bronze para uma fonte específica.")
    parser.add_argument(
        "--source",
        type=str,
        required=True,
        choices=SOURCE_CONFIGS.keys(),
        help="A fonte de dados para ingestão."
    )
    args = parser.parse_args()
    source_name = args.source

    print(f"Iniciando job de ingestão para a fonte: {source_name}")
    source_config = SOURCE_CONFIGS[source_name]

    spark = get_spark_session(app_name=f"{source_name.capitalize()}StreamingIngestion")

    streamer = KafkaToBronzeStreamer(spark=spark, source_config=source_config)

    try:
        streamer.run()
    except Exception as e:
        print(f"Ocorreu um erro durante o job de streaming para a fonte '{source_name}': {e}", file=sys.stderr)
    finally:
        print("Parando a sessão Spark.")
        spark.stop()


if __name__ == "__main__":
    main()