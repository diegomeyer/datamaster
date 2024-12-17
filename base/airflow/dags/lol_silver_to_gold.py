import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, sum, max, min,current_date

# Lê os argumentos do Airflow
silver_path_games = sys.argv[1]
silver_path_participants = sys.argv[2]
silver_path_teams_stats = sys.argv[3]
silver_path_teams_bans = sys.argv[4]
gold_path_match_summary = sys.argv[5]
gold_path_player_performance = sys.argv[6]
gold_path_team_performance = sys.argv[7]
partition_date = sys.argv[8]

# Criar a SparkSession
spark = SparkSession.builder \
    .appName("Transformação Silver para Gold") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.kryo.registrationRequired", "false")\
    .getOrCreate()

# Carregar as tabelas Silver
games_df = spark.read.parquet(f"{silver_path_games}/partition_date={partition_date}").withColumn("partition_date", current_date())
participants_df = spark.read.parquet(f"{silver_path_participants}/partition_date={partition_date}").withColumn("partition_date", current_date())
teams_stats_df = spark.read.parquet(f"{silver_path_teams_stats}/partition_date={partition_date}").withColumn("partition_date", current_date())
teams_bans_df = spark.read.parquet(f"{silver_path_teams_bans}/partition_date={partition_date}").withColumn("partition_date", current_date())

# Tabela 1: Resumo de partidas (match_summary)
match_summary_df = games_df.select(
    "match_id",
    "game_creation",
    "game_duration",
    "game_mode",
    "game_version",
    "map_id",
    "queue_id",
    "platform_id",
    "game_start_timestamp",
    "game_end_timestamp",
    "partition_date"
)

match_summary_df.dropDuplicates().write.mode("overwrite").partitionBy("partition_date").parquet(gold_path_match_summary)

# Tabela 2: Desempenho dos jogadores (player_performance)
player_performance_df = participants_df.groupBy("match_id", "participant_id", "champion_id", "champion_name", "team_id", "partition_date") \
    .agg(
        sum("kills").alias("total_kills"),
        sum("deaths").alias("total_deaths"),
        sum("assists").alias("total_assists"),
        sum("total_damage_dealt").alias("total_damage_dealt"),
        sum("total_damage_taken").alias("total_damage_taken"),
        sum("gold_earned").alias("total_gold_earned"),
        sum("wardsPlaced").alias("wards_placed"),
        sum("wardsKilled").alias("wards_killed"),
        sum("itemsPurchased").alias("items_purchased"),
        max("win").alias("win_status")
    )

player_performance_df.dropDuplicates().write.mode("overwrite").partitionBy("partition_date").parquet(gold_path_player_performance)

# Tabela 3: Desempenho do time (team_performance)
team_performance_df = teams_stats_df.groupBy("match_id", "team_id", "partition_date") \
    .agg(
        max("win").alias("win_status"),
        sum("baron_kills").alias("total_baron_kills"),
        sum("dragon_kills").alias("total_dragon_kills"),
        sum("tower_kills").alias("total_tower_kills")
    )

team_performance_df.dropDuplicates().write.mode("overwrite").partitionBy("partition_date").parquet(gold_path_team_performance)

# Exibir sucesso
print("Camada Gold criada com sucesso!")
