from pyspark.sql import SparkSession
from pyspark import SparkConf
import time

conf = SparkConf()
conf.set("spark.metrics.conf", "/etc/metrics/spark-metrics.properties")
conf.set("spark.ui.prometheus.enabled", "true")
conf.set("spark.metrics.namespace", "facebook_app")

spark = SparkSession.builder \
    .appName("FacebookIngestion") \
    .config(conf=conf) \
    .getOrCreate()

print("Spark application running. Waiting 120s to keep /metrics alive...")
time.sleep(120)