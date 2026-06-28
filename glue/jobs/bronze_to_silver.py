import sys
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import col

args = getResolvedOptions(sys.argv, ['JOB_NAME'])

sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Read Bronze layer
bronze_df = spark.read \
    .option("multiLine", "true") \
    .json("s3://youtube-analytics-lakehouse-smriti/bronze/youtube_trending/")

# Transform and clean
silver_df = bronze_df.select(
    col("id").alias("video_id"),
    col("snippet.title").alias("title"),
    col("snippet.channelId").alias("channel_id"),
    col("snippet.channelTitle").alias("channel_title"),
    col("snippet.categoryId").alias("category_id"),
    col("snippet.publishedAt").alias("published_at"),
    col("statistics.viewCount").cast("long").alias("view_count"),
    col("statistics.likeCount").cast("long").alias("like_count"),
    col("statistics.commentCount").cast("long").alias("comment_count"),
    col("contentDetails.duration").alias("duration"),
    col("region_code"),
    col("ingested_at")
).dropDuplicates(["video_id", "region_code", "ingested_at"]) \
 .filter(col("video_id").isNotNull())

# Write Silver layer as Parquet
silver_df.write \
    .mode("overwrite") \
    .partitionBy("region_code") \
    .parquet("s3://youtube-analytics-lakehouse-smriti/silver/youtube_trending/")

job.commit()