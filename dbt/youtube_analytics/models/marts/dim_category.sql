SELECT DISTINCT
    category_id
FROM {{ ref('stg_video_metrics') }}
WHERE category_id IS NOT NULL