WITH latest_snapshot AS (
    SELECT 
        video_id,
        region_code,
        MAX(ingested_at) as latest_ingested_at
    FROM {{ ref('stg_video_metrics') }}
    GROUP BY video_id, region_code
)
SELECT 
    s.video_id,
    s.channel_id,
    s.category_id,
    CAST(s.ingested_at AS DATE) as date_key,
    s.region_code,
    s.view_count,
    s.like_count,
    s.comment_count,
    s.duration,
    s.ingested_at
FROM {{ ref('stg_video_metrics') }} s
INNER JOIN latest_snapshot ls
    ON s.video_id = ls.video_id
    AND s.region_code = ls.region_code
    AND s.ingested_at = ls.latest_ingested_at