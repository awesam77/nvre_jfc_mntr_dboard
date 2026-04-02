# streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# Sample Data
# -----------------------------
data = {
    "Job Name": ["Customer_Data_Load", "Sales_Incremental_Load", "Inventory_Refresh", "User_Activity_Load", "Financial_Reports"],
    "Total Runs": [365, 360, 350, 340, 355],
    "Success %": [99, 88, 95, 92, 97],
    "Failures": [3, 12, 8, 27, 10],
    "Avg Duration (min)": [12, 20, 15, 18, 14],
    "Owner/Team": ["Team A", "Team B", "Team C", "Team A", "Team B"],
    "Manual Triggers": [0, 3, 2, 5, 1]
}

df = pd.DataFrame(data)

# -----------------------------
# Streamlit Layout
# -----------------------------
st.set_page_config(page_title="Databricks Yearly Job Report", layout="wide")
st.title("📊 Databricks Yearly Job Monitoring Report (2026)")

# -----------------------------
# Executive Summary
# -----------------------------
st.header("Executive Summary")
total_jobs = df["Total Runs"].sum()
overall_success = round((df["Success %"] * df["Total Runs"]).sum() / total_jobs, 2)
total_failures = df["Failures"].sum()
total_manual = df["Manual Triggers"].sum()

col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Job Runs", total_jobs)
col2.metric("Overall Success %", f"{overall_success}%")
col3.metric("Total Failures", total_failures)
col4.metric("Manual Triggers", total_manual)

# -----------------------------
# Top Performing & Problematic Jobs
# -----------------------------
st.header("Top Performing & Problematic Jobs")
st.dataframe(df.style.background_gradient(subset=["Success %"], cmap="Greens"))

# -----------------------------
# Charts
# -----------------------------
st.header("Charts & Trends")

# Success vs Failures Bar Chart
df_chart = df.melt(id_vars="Job Name", value_vars=["Success %", "Failures"], var_name="Metric", value_name="Value")
fig1 = px.bar(df_chart, x="Job Name", y="Value", color="Metric", barmode="group",
              title="Job Success % vs Failures", height=400)
st.plotly_chart(fig1, use_container_width=True)

# Average Duration Chart
fig2 = px.bar(df, x="Job Name", y="Avg Duration (min)", color="Avg Duration (min)",
              title="Average Job Duration (min)", height=400)
st.plotly_chart(fig2, use_container_width=True)

# Failures Heatmap (Optional)
fig3 = px.imshow(df[["Failures"]].T, text_auto=True,
                 labels=dict(x="Job Name", y="Metric", color="Failures"),
                 x=df["Job Name"], y=["Failures"], title="Failures Heatmap")
st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# Filters
# -----------------------------
st.header("Filters / Interactive Analysis")
team_filter = st.multiselect("Select Team", options=df["Owner/Team"].unique(), default=df["Owner/Team"].unique())
filtered_df = df[df["Owner/Team"].isin(team_filter)]
st.dataframe(filtered_df)

# Optionally, download filtered data
st.download_button(
    label="📥 Download Filtered Data as CSV",
    data=filtered_df.to_csv(index=False),
    file_name="databricks_yearly_report.csv",
    mime="text/csv"
)

st.info("🔹 This dashboard shows yearly trends for Databricks jobs including success rate, failures, manual triggers, and average durations. Color-coded charts and tables make it easy for stakeholders to review performance at a glance.")