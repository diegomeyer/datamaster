# Base image oficial do Spark 3.5.5 com Scala 2.12
FROM bitnami/spark:3.5.5

USER root

# Diretório para adicionar os JARs
RUN mkdir -p /opt/extra-jars
WORKDIR /opt/extra-jars

# JARs para Iceberg
ADD https://repo1.maven.org/maven2/org/apache/iceberg/iceberg-spark-runtime-3.4_2.12/1.4.0/iceberg-spark-runtime-3.4_2.12-1.4.0.jar .

# JARs para suporte a S3A (MinIO, AWS S3)
ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.6/hadoop-aws-3.3.6.jar .
ADD https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/3.3.6/hadoop-common-3.3.6.jar .
ADD https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.593/aws-java-sdk-bundle-1.12.593.jar .

# JARs para Kafka
ADD https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.5/spark-sql-kafka-0-10_2.12-3.5.5.jar .
ADD https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.5.1/kafka-clients-3.5.1.jar .

# Copie os JARs para o classpath do Spark
RUN mv /opt/extra-jars/*.jar /opt/bitnami/spark/jars/

# Ajustes finais (opcional: add bash, net-tools, etc)
RUN apt-get update && apt-get install -y curl vim net-tools

#USER 1001  # Volta ao usuário não-root do Spark

