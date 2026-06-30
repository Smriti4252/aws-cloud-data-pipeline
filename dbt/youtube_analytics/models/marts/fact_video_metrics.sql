SELECT
    video_id,
    channel_id,
    category_id,
    CAST(ingested_at AS DATE) AS date_key,
    region_code,
    view_count,
    like_count,
    comment_count,
    duration,
    ingested_at
FROM {{ ref('stg_video_metrics') }}