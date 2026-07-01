import streamlit as st
import snowflake.connector
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="YouTube Trend Intelligence", layout="wide")

@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        account=os.getenv("SNOWFLAKE_ACCOUNT"),
        user=os.getenv("SNOWFLAKE_USER"),
        password=os.getenv("SNOWFLAKE_PASSWORD"),
        warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
        database=os.getenv("SNOWFLAKE_DATABASE"),
        schema=os.getenv("SNOWFLAKE_SCHEMA"),
        role=os.getenv("SNOWFLAKE_ROLE")
    )

@st.cache_data(ttl=600)
def run_query(query):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query)
    df = cur.fetch_pandas_all()
    cur.close()
    return df

# Header
st.title("🎯 YouTube Trend Intelligence")
st.markdown("**Content strategy insights** — What to create, when to post, and where to grow")

# Region filter
region = st.selectbox("Select Region", ["ALL", "IN", "US", "GB"])
region_filter = f"AND f.region_code = '{region}'" if region != "ALL" else ""

st.divider()

# ── SECTION 1: NICHE INTELLIGENCE ──
st.header("📊 Niche Intelligence — What Content is Winning?")

niche_df = run_query(f"""
    SELECT 
        c.category_name,
        f.region_code,
        COUNT(DISTINCT f.video_id) as video_count,
        AVG(f.view_count) as avg_views,
        AVG(f.like_count) as avg_likes,
        AVG(f.comment_count) as avg_comments,
        AVG((f.like_count + f.comment_count) / NULLIF(f.view_count, 0)) * 100 as engagement_rate
    FROM youtube_analytics.presentation.fact_video_metrics f
    JOIN youtube_analytics.raw.category_mapping c 
        ON f.category_id = c.category_id
    WHERE f.view_count > 0
    {region_filter}
    GROUP BY c.category_name, f.region_code
    ORDER BY avg_views DESC
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🔥 Top Niches by Average Views")
    top_niches = niche_df.groupby('CATEGORY_NAME')['AVG_VIEWS'].mean().reset_index()
    top_niches = top_niches.sort_values('AVG_VIEWS', ascending=True).tail(10)
    fig = px.bar(top_niches, x='AVG_VIEWS', y='CATEGORY_NAME', orientation='h',
                 color='AVG_VIEWS', color_continuous_scale='Reds')
    fig.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("💬 Top Niches by Engagement Rate")
    eng_niches = niche_df.groupby('CATEGORY_NAME')['ENGAGEMENT_RATE'].mean().reset_index()
    eng_niches = eng_niches.sort_values('ENGAGEMENT_RATE', ascending=True).tail(10)
    fig2 = px.bar(eng_niches, x='ENGAGEMENT_RATE', y='CATEGORY_NAME', orientation='h',
                  color='ENGAGEMENT_RATE', color_continuous_scale='Blues')
    fig2.update_layout(showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig2, use_container_width=True)

# Insight Box
st.subheader("💡 Key Insights")
col1, col2, col3 = st.columns(3)

with col1:
    st.info("""
    **📈 High Views ≠ High Engagement**
    
    Film & Animation gets maximum views but Education & Comedy 
    have higher engagement rates — meaning niche audiences 
    are more active and loyal.
    """)

with col2:
    st.success("""
    **🎯 Creator Strategy**
    
    If you want VIEWS → Create Film/Entertainment content
    
    If you want ENGAGEMENT → Create Education/Comedy content
    
    High engagement = better for long-term channel growth
    """)

with col3:
    st.warning("""
    **🌍 Regional Opportunity**
    
    Filter by IN/US/GB above to see which categories 
    dominate each region — same content performs 
    very differently across markets.
    """)

st.divider()

# ── SECTION 2: BEST TIME TO POST ──
st.header("⏰ Best Time to Post — Upload Pattern Analysis")

time_df = run_query(f"""
    SELECT 
        EXTRACT(HOUR FROM s.published_at) as upload_hour,
        EXTRACT(DOW FROM s.published_at) as day_of_week,
        COUNT(DISTINCT f.video_id) as video_count,
        AVG(f.view_count) as avg_views
    FROM youtube_analytics.presentation.fact_video_metrics f
    JOIN youtube_analytics.presentation.stg_video_metrics s 
        ON f.video_id = s.video_id AND f.region_code = s.region_code
    WHERE s.published_at IS NOT NULL
    {region_filter}
    GROUP BY upload_hour, day_of_week
    ORDER BY avg_views DESC
""")

day_map = {0: 'Sunday', 1: 'Monday', 2: 'Tuesday', 3: 'Wednesday',
           4: 'Thursday', 5: 'Friday', 6: 'Saturday'}

if not time_df.empty:
    time_df['DAY_NAME'] = time_df['DAY_OF_WEEK'].map(day_map)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📅 Best Day to Upload")
        day_df = time_df.groupby('DAY_NAME')['AVG_VIEWS'].mean().reset_index()
        day_df = day_df.sort_values('AVG_VIEWS', ascending=False)
        fig3 = px.bar(day_df, x='DAY_NAME', y='AVG_VIEWS',
                      color='AVG_VIEWS', color_continuous_scale='Greens')
        fig3.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)

    with col2:
        st.subheader("🕐 Best Hour to Upload")
        hour_df = time_df.groupby('UPLOAD_HOUR')['AVG_VIEWS'].mean().reset_index()
        hour_df = hour_df.sort_values('AVG_VIEWS', ascending=False).head(10)
        fig4 = px.bar(hour_df, x='UPLOAD_HOUR', y='AVG_VIEWS',
                      color='AVG_VIEWS', color_continuous_scale='Oranges')
        fig4.update_layout(showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig4, use_container_width=True)

st.divider()

# ── SECTION 3: CROSS REGION OPPORTUNITY ──
st.header("🌍 Cross-Region Opportunity — Viral in Multiple Regions")

cross_df = run_query("""
    SELECT DISTINCT
        s.title,
        s.channel_title,
        f.region_code,
        f.view_count
    FROM youtube_analytics.presentation.fact_video_metrics f
    JOIN youtube_analytics.presentation.stg_video_metrics s 
        ON f.video_id = s.video_id 
        AND f.region_code = s.region_code
        AND f.ingested_at = s.ingested_at
    WHERE f.video_id IN (
        SELECT video_id 
        FROM youtube_analytics.presentation.fact_video_metrics
        GROUP BY video_id
        HAVING COUNT(DISTINCT region_code) > 1
    )
    ORDER BY f.view_count DESC
    LIMIT 20
""")

if not cross_df.empty:
    st.markdown("**Videos trending in multiple regions simultaneously:**")
    
    pivot_df = cross_df.pivot_table(
        index='TITLE', columns='REGION_CODE',
        values='VIEW_COUNT', aggfunc='max'
    ).reset_index()
    st.dataframe(pivot_df, use_container_width=True)

st.divider()

# ── SECTION 4: CREATOR INTELLIGENCE ──
st.header("📺 Creator Intelligence — Who is Consistently Trending?")

creator_df = run_query(f"""
    SELECT 
        s.channel_title,
        COUNT(DISTINCT f.video_id) as trending_videos,
        COUNT(DISTINCT f.region_code) as regions_trending,
        SUM(f.view_count) as total_views,
        AVG(f.view_count) as avg_views_per_video,
        AVG((f.like_count + f.comment_count) / NULLIF(f.view_count, 0)) * 100 as engagement_rate
    FROM youtube_analytics.presentation.fact_video_metrics f
    JOIN youtube_analytics.presentation.stg_video_metrics s 
        ON f.video_id = s.video_id AND f.region_code = s.region_code
    WHERE f.view_count > 0
    {region_filter}
    GROUP BY s.channel_title
    HAVING COUNT(DISTINCT f.video_id) >= 2
    ORDER BY trending_videos DESC, total_views DESC
    LIMIT 15
""")

col1, col2 = st.columns(2)

with col1:
    st.subheader("🏆 Most Consistent Channels")
    fig5 = px.bar(creator_df.head(10), x='TRENDING_VIDEOS', y='CHANNEL_TITLE',
                  orientation='h', color='REGIONS_TRENDING',
                  color_continuous_scale='Viridis')
    fig5.update_layout(coloraxis_showscale=False)
    st.plotly_chart(fig5, use_container_width=True)

with col2:
    st.subheader("📈 Engagement vs Views")
    fig6 = px.scatter(creator_df, x='AVG_VIEWS_PER_VIDEO', y='ENGAGEMENT_RATE',
                      hover_name='CHANNEL_TITLE', size='TRENDING_VIDEOS',
                      color='REGIONS_TRENDING')
    fig6.update_layout(showlegend=False)
    st.plotly_chart(fig6, use_container_width=True)

st.divider()
st.caption("Data refreshed every 6 hours via AWS Lambda | Pipeline: S3 → Glue → Snowflake → dbt")