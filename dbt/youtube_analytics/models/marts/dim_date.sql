SELECT DISTINCT
    CAST(ingested_at AS DATE) AS date_key,
    EXTRACT(YEAR FROM ingested_at) AS year,
    EXTRACT(MONTH FROM ingested_at) AS month,
    EXTRACT(DAY FROM ingested_at) AS day,
    EXTRACT(DOW FROM ingested_at) AS day_of_week
FROM {{ ref('stg_video_metrics') }}
WHERE ingested_at IS NOT NULL