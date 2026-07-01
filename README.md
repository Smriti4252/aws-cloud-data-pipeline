A production-style cloud data pipeline that automatically collects YouTube trending data, processes it through a Medallion Architecture, models it into a dimensional warehouse, and exposes business intelligence through an interactive dashboard.

---




## 🏗️ Architecture

```mermaid
flowchart LR

subgraph Ingestion
A[YouTube Data API<br/>IN • US • GB]
B[EventBridge Scheduler<br/>Every 6 Hours]
C[AWS Lambda<br/>Ingestion]
D[S3 Bronze Layer<br/>Raw JSON]
end

subgraph Transformation
E[AWS Glue ETL<br/>JSON → Parquet]
F[S3 Silver Layer<br/>Clean Parquet]
G[Snowflake<br/>Raw Warehouse]
H[dbt<br/>Star Schema]
end

subgraph Analytics
I[Streamlit Dashboard<br/>Business Intelligence]
end

subgraph Infrastructure
J[AWS IAM<br/>Least Privilege Access]
end

A --> B
B --> C
C --> D
D --> E
E --> F
F --> G
G --> H
H --> I

J -.-> C
J -.-> E
J -.-> G
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

Raw JSON responses from the YouTube API are stored exactly as received without any transformations. Data is partitioned by ingestion timestamp to simplify reprocessing and historical analysis.

### Silver Layer

AWS Glue ETL jobs clean, standardize, and convert raw JSON into optimized Parquet files.

Transformations include:

* Schema normalization
* Type casting (`viewCount`, `likeCount`, `commentCount` → LONG)
* Deduplication using `video_id + region_code + ingested_at`
* Null filtering
* Standardized column naming

### Gold Layer — Snowflake + dbt

Business-ready dimensional models are built using dbt following a Star Schema approach.

```text
fact_video_metrics
├── dim_channel
├── dim_category
├── dim_date
└── dim_region
```

The fact table captures the performance of a video within a specific region at a particular ingestion timestamp.

---

## 📊 Dashboard — Business Intelligence

The Streamlit dashboard answers real content strategy questions:

* **Niche Intelligence** — Which content categories receive the highest views versus engagement?
* **Best Time to Post** — Which day and hour maximize reach?
* **Cross-Region Opportunity** — Which videos trend across multiple regions simultaneously?
* **Creator Intelligence** — Which channels consistently appear in trending lists?
* **Category Momentum** — Which categories are growing fastest over time?
* **Regional Preferences** — How does audience behavior differ between countries?

---

## 📷 Dashboard Preview

### 🎯 Niche Intelligence

Compare categories by average views and engagement rate to understand which content performs best.


<img width="1860" height="971" alt="image" src="https://github.com/user-attachments/assets/1099fd51-0d59-401f-82fd-c00765c27a06" />


---

### ⏰ Best Time to Post

Identify the best day and hour to publish content based on historical trending performance.

<img width="1847" height="742" alt="image" src="https://github.com/user-attachments/assets/52c7cb80-58fd-4f83-852f-2c7d0d5f6ad4" />


---

### 🌍 Cross-Region Opportunity

Find videos that trend across multiple countries simultaneously and identify global content opportunities.

<img width="1818" height="551" alt="image" src="https://github.com/user-attachments/assets/9436aab2-ac80-49a2-a986-fd303a7d8383" />




---

### 📺 Creator Intelligence

Analyze channels that consistently appear in trending lists and compare engagement against audience reach.

<img width="1783" height="672" alt="image" src="https://github.com/user-attachments/assets/a01367e7-a75a-4685-a562-49934c297d2e" />


---

## 🧪 Data Quality

dbt tests implemented:

* `not_null` — `video_id`, `region_code`
* `accepted_values` — `region_code` in `['IN', 'US', 'GB']`
* `unique_combination` — `video_id + region_code + ingested_at`

---

## 📁 Repository Structure

```text
aws-cloud-data-pipeline/
├── images/
│   ├── architecture.png
│   ├── niche_intelligence.png
│   ├── best_time_to_post.png
│   ├── cross_region_opportunity.png
│   └── creator_intelligence.png
│
├── ingestion/
│   └── lambda/
│       └── handler.py
│
├── glue/
│   └── jobs/
│       └── bronze_to_silver.py
│
├── dbt/
│   └── youtube_analytics/
│       ├── models/
│       │   ├── staging/
│       │   └── marts/
│       └── packages.yml
│
├── streamlit/
│   └── app.py
│
├── infrastructure/
│   └── snowflake/
│       └── setup.sql
│
└── .github/
    └── workflows/
```

---

## 🚀 Pipeline Flow

1. **EventBridge Scheduler** triggers the ingestion process every 6 hours.
2. **AWS Lambda** fetches the top 50 trending videos from India, United States, and United Kingdom using the YouTube Data API.
3. Raw JSON responses are stored in the **S3 Bronze Layer** using timestamp-based partitions.
4. **AWS Glue ETL** reads Bronze data, applies transformations, and writes optimized Parquet files to the **S3 Silver Layer**.
5. **Snowflake COPY INTO** loads Silver Parquet files into warehouse tables.
6. **dbt run** builds dimensional models and business-ready marts.
7. **Streamlit** queries Snowflake models to power the analytics dashboard.

---

## 📈 Data Volume

* 150 videos collected per pipeline execution
* 50 videos per region across IN, US, and GB
* Pipeline runs every 6 hours
* 4 ingestion cycles per day
* 600 records generated daily
* 1,900+ historical video-region snapshots currently available for analysis

---

## 🌍 Regions Covered

| Region | Code |
|--------|------|
| India | IN |
| United States | US |
| United Kingdom | GB |

---

## 🎯 Project Goals

This project was built to simulate a real-world cloud analytics platform using modern data engineering practices.

The pipeline demonstrates:

* Event-driven ingestion
* Lakehouse architecture
* Batch ETL processing with PySpark
* Dimensional modeling with dbt
* Data quality testing
* Cloud-native analytics delivery

The objective was to build an end-to-end system that covers the complete data lifecycle from ingestion to business intelligence reporting.
