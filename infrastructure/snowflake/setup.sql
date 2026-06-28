-- Database aur Schema
CREATE DATABASE youtube_analytics;
USE DATABASE youtube_analytics;
CREATE SCHEMA raw;
CREATE SCHEMA presentation;

-- Warehouse
CREATE WAREHOUSE youtube_wh
  WAREHOUSE_SIZE = 'X-SMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;

USE WAREHOUSE youtube_wh;

-- Raw table jahan S3 Silver data aayega
CREATE OR REPLACE TABLE youtube_analytics.raw.video_metrics (
    video_id        VARCHAR,
    title           VARCHAR,
    channel_id      VARCHAR,
    channel_title   VARCHAR,
    category_id     VARCHAR,
    published_at    VARCHAR,
    view_count      NUMBER,
    like_count      NUMBER,
    comment_count   NUMBER,
    duration        VARCHAR,
    region_code     VARCHAR,
    ingested_at     VARCHAR
);