import pandas as pd
import streamlit as st
import plotly.express as px
from analytics import load_data, pipeline_reliability, yearly_report

st.set_page_config(page_title="Pipeline Monitoring Dashboard", layout="wide")

st.title("📊 Novare Pipeline Monitoring Dashboard")

df = load_data()
    
st.subheader("✅ Key Metrics")

total_runs = len(df)
success_count = (df.status=='Success').sum()
fail_count = (df.status=='Failed').sum()
success_rate = success_count / total_runs * 100
avg_runtime = df['duration_seconds'].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Runs", total_runs)
col2.metric("Successful Runs", success_count)
col3.metric("Failed Runs", fail_count)
col4.metric("Success Rate", f"{success_rate:.2f}%")

st.subheader("⏱ Duration Analysis")
fig_duration = px.histogram(df, x="duration_seconds", nbins=30, title="Pipeline Duration Distribution (seconds)")
st.plotly_chart(fig_duration, use_container_width=True)

st.subheader("🔥 Top 10 Failing Pipelines")
top_failing = df[df.status=='Failed'].groupby('pipeline_name').size().sort_values(ascending=False).head(10)
st.bar_chart(top_failing)

st.subheader("📅 Monthly Success Rate")
df['month'] = df['run_date'].dt.to_period('M').astype(str)

monthly_stats = df.groupby('month')['status'].value_counts().unstack(fill_value=0)
monthly_stats['success_rate'] = monthly_stats.get('Success', 0) / (monthly_stats.get('Success', 0) + monthly_stats.get('Failed', 0)) * 100
fig_monthly = px.line(monthly_stats, y='success_rate', title="Monthly Success Rate (%)", markers=True)
st.plotly_chart(fig_monthly, use_container_width=True)

st.subheader("👤 Owner Performance")
owner_perf = df.groupby(['owner', 'status']).size().unstack(fill_value=0)
owner_perf['success_rate'] = owner_perf.get('Success', 0) / (owner_perf.get('Success', 0) + owner_perf.get('Failed', 0)) * 100
st.dataframe(owner_perf)

# st.success("✅ Report generated successfully!")