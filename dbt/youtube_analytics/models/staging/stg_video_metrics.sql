SELECT
    video_id,
    title,
    channel_id,
    channel_title,
    category_id,
    TRY_TO_TIMESTAMP(published_at) AS published_at,
    view_count,
    like_count,
    comment_count,
    duration,
    region_code,
    TRY_TO_TIMESTAMP(ingested_at) AS ingested_at
FROM {{ source('raw', 'video_metrics') }}
WHERE video_id IS NOT NULL