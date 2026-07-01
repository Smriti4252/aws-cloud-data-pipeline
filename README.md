# 🎯 YouTube Analytics Lakehouse

A production-style cloud data pipeline that automatically collects YouTube trending data, processes it through a Medallion Architecture, models it into a dimensional warehouse, and exposes business intelligence through an interactive dashboard.

---

## 🏗️ Architecture

```
YouTube Data API
      ↓
AWS EventBridge Scheduler (every 6 hours)
      ↓
AWS Lambda (Ingestion)
      ↓
AWS S3 — Bronze Layer (raw JSON)
      ↓
AWS Glue ETL (transformation)
      ↓
AWS S3 — Silver Layer (Parquet)
      ↓
Snowflake Data Warehouse
      ↓
dbt (Star Schema Modeling)
      ↓
Streamlit Dashboard (Business Intelligence)
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Ingestion | AWS Lambda, YouTube Data API v3 |
| Orchestration | AWS EventBridge Scheduler |
| Storage | AWS S3 (Bronze + Silver) |
| Transformation | AWS Glue (PySpark) |
| Data Warehouse | Snowflake |
| Data Modeling | dbt (Star Schema) |
| Dashboard | Streamlit + Plotly |
| Infrastructure | AWS IAM |
| Version Control | GitHub |

---

## 📐 Medallion Architecture

### Bronze Layer
Raw JSON responses from YouTube API stored exactly as received. Partitioned by ingestion timestamp.

### Silver Layer
Cleaned and standardized Parquet files via AWS Glue ETL:
- Schema normalization
- Type casting (viewCount, likeCount → LONG)
- Deduplication by `video_id + region_code + ingested_at`
- Null filtering

### Gold Layer — Snowflake + dbt
Business-ready dimensional model:

```
fact_video_metrics
├── dim_channel
├── dim_category
├── dim_date
└── dim_region
```

---

## 📊 Dashboard — Business Intelligence

The Streamlit dashboard answers real content strategy questions:

- **Niche Intelligence** — Which content categories get most views vs highest engagement?
- **Best Time to Post** — Which day and hour maximizes reach?
- **Cross-Region Opportunity** — Which videos are trending across IN/US/GB simultaneously?
- **Creator Intelligence** — Which channels consistently appear in trending?

---

## 🔑 Key Engineering Decisions

**Why Lambda over EC2?**
Ingestion runs every 6 hours and takes ~6 seconds. Serverless eliminates idle compute cost — Lambda costs nearly $0 for this workload vs EC2 running 24/7.

**Why Glue over local PySpark?**
Glue provides managed Spark without cluster setup, integrates natively with S3 and Glue Data Catalog, and scales automatically.

**Why Parquet in Silver Layer?**
Columnar format enables faster analytical queries compared to JSON. Snowflake COPY INTO reads Parquet natively without transformation overhead.

**Why dbt for modeling?**
dbt brings software engineering practices to SQL — version control, testing, documentation. Data quality tests run automatically on every model refresh.

**Fact Table Grain Decision:**
Initial assumption was video_id = unique key. Discovered via dbt uniqueness test that same video appears across multiple regions AND multiple ingestion snapshots. Correct grain is `video_id + region_code + ingested_at` — each row represents one video in one region at one point in time.

---

## 🧪 Data Quality

dbt tests implemented:
- `not_null` — video_id, region_code
- `accepted_values` — region_code in ['IN', 'US', 'GB']
- `unique_combination` — video_id + region_code + ingested_at

---

## 📁 Repository Structure

```
aws-cloud-data-pipeline/
├── ingestion/
│   └── lambda/
│       └── handler.py
├── glue/
│   └── jobs/
│       └── bronze_to_silver.py
├── dbt/
│   └── youtube_analytics/
│       ├── models/
│       │   ├── staging/
│       │   └── marts/
│       └── packages.yml
├── streamlit/
│   └── app.py
├── infrastructure/
│   └── snowflake/
│       └── setup.sql
└── .github/
    └── workflows/
```

---

## 🚀 Pipeline Flow

1. **EventBridge** triggers Lambda every 6 hours
2. **Lambda** fetches top 50 trending videos from IN, US, GB via YouTube Data API
3. Raw JSON landed in **S3 Bronze** with timestamp-based paths
4. **Glue ETL** reads Bronze JSON, cleans and transforms, writes **S3 Silver** as Parquet
5. **Snowflake COPY INTO** loads Silver Parquet into raw schema
6. **dbt run** builds star schema in presentation schema
7. **Streamlit** dashboard reads from Snowflake presentation layer

---

## 📈 Data Volume

- 150 videos per run (50 per region × 3 regions — IN, US, GB)
- Pipeline runs every 6 hours
- 1,912 unique video-region snapshots currently loaded
