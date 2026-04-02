import streamlit as st
import plotly.express as px
from analytics import load_data, pipeline_reliability, yearly_report

st.title("Pipeline Monitoring Dashboard")

df = load_data()

#display raw data
# st.subheader("Raw Data")
# st.dataframe(df)

top_failing = (
    df[df.status=='FAILED']
    .groupby('pipeline_name')
    .size()
    .sort_values(ascending=False)
)

monthly_stats = (
    df.groupby(df['run_date'].dt.month)
      .status.value_counts()
      .unstack(fill_value=0)
)
monthly_stats['success_rate'] = monthly_stats['Success'] / (monthly_stats['Success'] + monthly_stats['Failed']) * 100
# Status summary
status_count = df.groupby("status").size().reset_index(name="count")

fig = px.pie(
    status_count,
    values="count",
    names="status",
    title="Pipeline Success vs Failure"
)

st.plotly_chart(fig)

# Yearly report
yearly = yearly_report(df)

fig2 = px.bar(
    yearly,
    x="year",
    y="count",
    color="status",
    title="Yearly Pipeline Performance"
)

st.plotly_chart(fig2)

# Reliability score
st.subheader("Pipeline Reliability")

reliability = pipeline_reliability(df)

fig3 = px.bar(
    reliability,
    x="pipeline_name",
    y="reliability_score",
    title="Pipeline Reliability Score (%)"
)

st.plotly_chart(fig3)

import pandas as pd

# Assuming df is your cleaned DataFrame
total_runs = len(df)
success_count = (df.status=='Success').sum()
fail_count = (df.status=='Failed').sum()
success_rate = success_count / total_runs * 100

print(df.head(1))
avg_runtime = df['duration_seconds'].mean()
max_runtime = df['duration_seconds'].max()
min_runtime = df['duration_seconds'].min()

top_failing = df[df.status=='Failed'].groupby('pipeline_name').size().sort_values(ascending=False)

owner_perf = df.groupby(['owner', 'status']).size().unstack(fill_value=0)

print("===== Business Pipeline Report =====")
print(f"Total runs: {total_runs}")
print(f"Successful runs: {success_count}")
print(f"Failed runs: {fail_count}")
print(f"Success rate: {success_rate:.2f}%")
print(f"Average runtime: {avg_runtime:.0f} sec")
print(f"Max runtime: {max_runtime:.0f} sec")
print(f"Min runtime: {min_runtime:.0f} sec")
print("\nTop failing pipelines:")
print(top_failing.head(10))
print("\nOwner performance:")
print(owner_perf)

#streamlit run dashboard.py