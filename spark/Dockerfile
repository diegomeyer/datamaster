# Base image oficial do Spark 3.5.5 com Scala 2.12
FROM tabulario/spark-iceberg

#Hadoop
RUN wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar -P ${SPARK_HOME}/jars/
RUN wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client/3.3.4/hadoop-client-3.3.4.jar -P ${SPARK_HOME}/jars/
RUN wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client-runtime/3.3.4/hadoop-client-runtime-3.3.4.jar -P ${SPARK_HOME}/jars/
RUN wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client-api/3.3.4/hadoop-client-api-3.3.4.jar -P ${SPARK_HOME}/jars/

#AWS
RUN wget -q https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.901/aws-java-sdk-bundle-1.11.901.jar -P ${SPARK_HOME}/jars/

#Kafka
RUN wget -q https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.5/spark-sql-kafka-0-10_2.12-3.5.5.jar -P ${SPARK_HOME}/jars/
RUN wget -q https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.5.1/kafka-clients-3.5.1.jar -P ${SPARK_HOME}/jars/



##Hadoop
#RUN wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.6/hadoop-aws-3.3.6.jar -P ${SPARK_HOME}/jars/
#RUN wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client/3.3.6/hadoop-client-3.3.6.jar -P ${SPARK_HOME}/jars/
#RUN wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client-runtime/3.3.6/hadoop-client-runtime-3.3.6.jar -P ${SPARK_HOME}/jars/
#RUN wget -q https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client-api/3.3.6/hadoop-client-api-3.3.6.jar -P ${SPARK_HOME}/jars/
#
##AWS
#RUN wget -q https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.11.901/aws-java-sdk-bundle-1.11.901.jar -P ${SPARK_HOME}/jars/
##RUN wget -q https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.607/aws-java-sdk-bundle-1.12.607.jar -P ${SPARK_HOME}/jars/
##Kafka
#RUN wget -q https://repo1.maven.org/maven2/org/apache/spark/spark-sql-kafka-0-10_2.12/3.5.5/spark-sql-kafka-0-10_2.12-3.5.5.jar -P ${SPARK_HOME}/jars/
#RUN wget -q https://repo1.maven.org/maven2/org/apache/kafka/kafka-clients/3.5.1/kafka-clients-3.5.1.jar -P ${SPARK_HOME}/jars/
#
#RUN rm /opt/spark/jars/hadoop-client-runtime-3.3.4.jar
#RUN rm /opt/spark/jars/hadoop-client-api-3.3.4.jar
##RUN rm /opt/spark/jars/aws-java-sdk-bundle-1.11.901.jar


ENTRYPOINT ["./entrypoint.sh"]
CMD ["notebook"]