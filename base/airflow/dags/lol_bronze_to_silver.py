import sys
from pyspark.sql.functions import from_unixtime, to_date
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, from_json, row_number,current_date
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, LongType, ArrayType
from pyspark.sql.window import Window

# # Lê os argumentos do Airflow

bronze_path = sys.argv[1]
silver_path_games = sys.argv[2]
silver_path_participants = sys.argv[3]
silver_path_teams_stats = sys.argv[4]
silver_path_teams_bans = sys.argv[5]
partition_date = sys.argv[6]

print(partition_date)
# Criar a SparkSession
spark = SparkSession.builder \
    .appName("Transformação Bronze para Silver") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.kryo.registrationRequired", "false")\
    .getOrCreate()

# Carregar a camada Bronze
bronze_path = bronze_path
bronze_df = spark.read.parquet(f"{bronze_path}/partition_date={partition_date}")

# Definir o schema do JSON com base na estrutura dos dados
# Definir o schema do JSON com base na estrutura dos dados
json_schema = StructType([
    StructField("metadata", StructType([
        StructField("dataVersion", StringType(), True),
        StructField("matchId", StringType(), True),
        StructField("participants", ArrayType(StringType()), True)
    ]), True),
    StructField("info", StructType([
        StructField("gameId", LongType(), True),
        StructField("gameCreation", LongType(), True),
        StructField("gameDuration", IntegerType(), True),
        StructField("gameMode", StringType(), True),
        StructField("gameVersion", StringType(), True),
        StructField("mapId", IntegerType(), True),
        StructField("queueId", IntegerType(), True),
        StructField("platformId", StringType(), True),
        StructField("gameStartTimestamp", LongType(), True),
        StructField("gameEndTimestamp", LongType(), True),
        StructField("participants", ArrayType(
            StructType([
                StructField("championId", IntegerType(), True),
                StructField("championName", StringType(), True),
                StructField("teamId", IntegerType(), True),
                StructField("individualPosition", StringType(), True),
                StructField("lane", StringType(), True),
                StructField("kills", IntegerType(), True),
                StructField("deaths", IntegerType(), True),
                StructField("assists", IntegerType(), True),
                StructField("totalDamageDealt", IntegerType(), True),
                StructField("totalDamageTaken", IntegerType(), True),
                StructField("goldEarned", IntegerType(), True),
                StructField("win", StringType(), True),
                StructField("item0",IntegerType(),True),
                StructField("item1",IntegerType(),True),
                StructField("item2",IntegerType(),True),
                StructField("item3",IntegerType(),True),
                StructField("item4",IntegerType(),True),
                StructField("item5",IntegerType(),True),
                StructField("item6",IntegerType(),True),
                StructField("allInPings",IntegerType(),True),
                StructField("itemsPurchased",IntegerType(),True),
                StructField("wardsKilled",IntegerType(),True),
                StructField("wardsPlaced",IntegerType(),True),
            ])
        )),
        StructField("teams", ArrayType(
            StructType([
                StructField("teamId", IntegerType(), True),
                StructField("win", StringType(), True),
                StructField("objectives", StructType([
                    StructField("baron", StructType([
                        StructField("kills", IntegerType(), True)
                    ])),
                    StructField("dragon", StructType([
                        StructField("kills", IntegerType(), True)
                    ])),
                    StructField("tower", StructType([
                        StructField("kills", IntegerType(), True)
                    ]))
                ])),
                StructField("bans", ArrayType(
                    StructType([
                        StructField("pickTurn", IntegerType(), True),
                        StructField("championId", IntegerType(), True)
                    ])
                ))
            ])
        ))
    ])
    )
])
# Parsear o JSON da coluna json_data
parsed_df = bronze_df.withColumn("match_details", from_json(col("match_details"), json_schema)).select("match_details.*")
parsed_df = parsed_df.withColumn("partition_date", current_date())

match_summary_df = parsed_df.select(
    col("info.gameId").alias("match_id"),
    col("info.gameCreation").alias("game_creation"),
    col("info.gameDuration").alias("game_duration"),
    col("info.gameMode").alias("game_mode"),
    col("info.gameVersion").alias("game_version"),
    col("info.mapId").alias("map_id"),
    col("info.queueId").alias("queue_id"),
    col("info.platformId").alias("platform_id"),
    col("info.gameStartTimestamp").alias("game_start_timestamp"),
    col("info.gameEndTimestamp").alias("game_end_timestamp"),
    col("partition_date")
)

match_summary_df.dropDuplicates().write.mode("overwrite").partitionBy("partition_date").parquet(silver_path_games)

participant_window = Window.partitionBy("match_id").orderBy(col("participant.championId"))

participants_df = parsed_df.select(
    col("info.gameId").alias("match_id"),
    explode(col("info.participants")).alias("participant"),
    col("partition_date")
).select(
    col("match_id"),
    row_number().over(participant_window).alias("participant_id"),
    col("participant.championId").alias("champion_id"),
    col("participant.championName").alias("champion_name"),
    col("participant.teamId").alias("team_id"),
    col("participant.individualPosition").alias("individual_position"),
    col("participant.lane"),
    col("participant.kills"),
    col("participant.deaths"),
    col("participant.assists"),
    col("participant.item0"),
    col("participant.item1"),
    col("participant.item2"),
    col("participant.item3"),
    col("participant.item4"),
    col("participant.item5"),
    col("participant.item6"),
    col("participant.allInPings"),
    col("participant.itemsPurchased"),
    col("participant.wardsKilled"),
    col("participant.wardsPlaced"),
    col("participant.totalDamageDealt").alias("total_damage_dealt"),
    col("participant.totalDamageTaken").alias("total_damage_taken"),
    col("participant.goldEarned").alias("gold_earned"),
    col("participant.win"),
    col("partition_date")
)


participants_df.dropDuplicates().write.mode("overwrite").partitionBy("partition_date").parquet(silver_path_participants)


team_stats_df = parsed_df.select(
    col("info.gameId").alias("match_id"),
    explode(col("info.teams")).alias("team"),
    col("partition_date")
).select(
    col("match_id"),
    col("team.teamId").alias("team_id"),
    col("team.win"),
    col("team.objectives.baron.kills").alias("baron_kills"),
    col("team.objectives.dragon.kills").alias("dragon_kills"),
    col("team.objectives.tower.kills").alias("tower_kills"),
    col("partition_date")
)

team_stats_df.dropDuplicates().write.mode("overwrite").partitionBy("partition_date").parquet(silver_path_teams_stats)

team_bans_df = parsed_df.select(
    col("info.gameId").alias("match_id"),
    explode(col("info.teams")).alias("team"),
    col("partition_date")
).select(
    col("match_id"),
    col("team.teamId").alias("team_id"),
    explode(col("team.bans")).alias("ban"),
    col("partition_date")
).select(
    col("match_id"),
    col("team_id"),
    col("ban.pickTurn").alias("ban_turn"),
    col("ban.championId").alias("champion_id"),
    col("partition_date")
)

team_bans_df.dropDuplicates().write.mode("overwrite").partitionBy("partition_date").parquet(silver_path_teams_bans)