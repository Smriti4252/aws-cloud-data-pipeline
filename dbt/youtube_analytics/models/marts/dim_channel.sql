SELECT DISTINCT
    channel_id,
    channel_title
FROM {{ ref('stg_video_metrics') }}
WHERE channel_id IS NOT NULL