# streamlit_app_with_dates.py

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# -----------------------------
# Sample Data with Run Date
# -----------------------------
data = {
    "Job Name": ["Customer_Data_Load", "Sales_Incremental_Load", "Inventory_Refresh", "User_Activity_Load", "Financial_Reports"] * 12,
    "Total Runs": [30, 28, 29, 27, 30] * 12,
    "Success %": [99, 88, 95, 92, 97] * 12,
    "Failures": [0, 2, 1, 3, 1] * 12,
    "Avg Duration (min)": [12, 20, 15, 18, 14] * 12,
    "Owner/Team": ["Team A", "Team B", "Team C", "Team A", "Team B"] * 12,
    "Manual Triggers": [0, 1, 0, 2, 1] * 12,
    # "Run Date": pd.date_range(start="2026-01-01", periods=60, freq="M").tolist() * 5,
    "Run Date": pd.date_range(start="2026-01-01", periods=60, freq="M")
}

df = pd.DataFrame(data)

# -----------------------------
# Streamlit Layout
# -----------------------------
st.set_page_config(page_title="Databricks Yearly Job Report", layout="wide")
st.title("📊 Databricks Yearly Job Monitoring Report (2026)")

# -----------------------------
# Date Filter
# -----------------------------
st.sidebar.header("Filter Options")
start_date = st.sidebar.date_input("Start Date", df["Run Date"].min())
end_date = st.sidebar.date_input("End Date", df["Run Date"].max())

# Filter dataframe by date
filtered_df = df[(df["Run Date"] >= pd.to_datetime(start_date)) & (df["Run Date"] <= pd.to_datetime(end_date))]

# -----------------------------
# Executive Summary
# -----------------------------
st.header("Executive Summary")
total_jobs = filtered_df["Total Runs"].sum()
overall_success = round((filtered_df["Success %"] * filtered_df["Total Runs"]).sum() / total_jobs, 2) if total_jobs > 0 else 0
total_failures = filtered_df["Failures"].sum()
total_manual = filtered_df["Manual Triggers"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Job Runs", total_jobs)
col2.metric("Overall Success %", f"{overall_success}%")
col3.metric("Total Failures", total_failures)
col4.metric("Manual Triggers", total_manual)

# -----------------------------
# Top Performing & Problematic Jobs
# -----------------------------
st.header("Top Performing & Problematic Jobs")
st.dataframe(filtered_df.groupby("Job Name").agg({
    "Total Runs": "sum",
    "Success %": "mean",
    "Failures": "sum",
    "Avg Duration (min)": "mean",
    "Owner/Team": "first",
    "Manual Triggers": "sum"
}).sort_values(by="Failures", ascending=False).style.background_gradient(subset=["Success %"], cmap="Greens"))

# -----------------------------
# Charts & Trends
# -----------------------------
st.header("Charts & Trends")

# Success vs Failures
df_chart = filtered_df.groupby("Job Name").agg({"Success %": "mean", "Failures": "sum"}).reset_index()
df_chart_melt = df_chart.melt(id_vars="Job Name", var_name="Metric", value_name="Value")
fig1 = px.bar(df_chart_melt, x="Job Name", y="Value", color="Metric", barmode="group",
              title="Job Success % vs Failures", height=400)
st.plotly_chart(fig1, use_container_width=True)

# Average Duration Chart
fig2 = px.bar(filtered_df.groupby("Job Name")["Avg Duration (min)"].mean().reset_index(),
              x="Job Name", y="Avg Duration (min)", color="Avg Duration (min)",
              title="Average Job Duration (min)", height=400)
st.plotly_chart(fig2, use_container_width=True)

# Failures Heatmap
fig3 = px.imshow(filtered_df.groupby("Job Name")["Failures"].sum().to_frame().T, text_auto=True,
                 labels=dict(x="Job Name", y="Metric", color="Failures"),
                 x=filtered_df["Job Name"].unique(), y=["Failures"], title="Failures Heatmap")
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# Team Filter
# -----------------------------
team_filter = st.sidebar.multiselect("Select Team", options=df["Owner/Team"].unique(), default=df["Owner/Team"].unique())
final_df = filtered_df[filtered_df["Owner/Team"].isin(team_filter)]
st.header("Filtered Data")
st.dataframe(final_df)

# Download
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=final_df.to_csv(index=False),
    file_name="databricks_yearly_report_filtered.csv",
    mime="text/csv"
)

st.info("🔹 Use the sidebar to filter by date range and team. Charts and tables update dynamically based on your selection.")