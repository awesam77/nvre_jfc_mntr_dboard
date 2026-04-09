import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from analytics import load_data
import matplotlib.pyplot as plt


current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
# df = load_data()
df = pd.read_csv("data_uploads/pipeline_runs_202604021718.csv")


pipeline_names = df["pipeline_name"].drop_duplicates().tolist()
run_dates = pd.date_range(start="2026-01-01", periods=len(pipeline_names), freq="D")

total_runs_list = []
total_success_list = []
total_failed_list = []
avg_duration_list = []
manual_triggers_list = []
owner_list = []

for pipeline in pipeline_names:
    total_runs = df[df["pipeline_name"] == pipeline].shape[0]
    # success_runs = df[(df["pipeline_name"] == pipeline) & (df["status"] == "Success")].shape[0]


    failed_runs = df[(df["pipeline_name"] == pipeline) & (df["status"] == "Failed")].shape[0]
    pipeline_df = df[df["pipeline_name"] == pipeline]
    total_runs = pipeline_df.shape[0]
    total_success = pipeline_df[pipeline_df["status"] == "Success"].shape[0]
    success_percent = (total_success / total_runs) * 100 if total_runs > 0 else 0
    avg_duration = pipeline_df["duration_seconds"].mean() / 60  # convert seconds to minutes
    manual_triggers = pipeline_df[pipeline_df["run_type"] == "Manual Re-run"].shape[0]
    manual_triggers_list.append(manual_triggers)
    avg_duration_list.append(avg_duration)
    total_runs_list.append(int(total_runs))

    total_success_list.append(success_percent)
    total_failed_list.append(int(failed_runs))
    
    owner = pipeline_df["owner"].iloc[0]  # or "team" if your column is named differently
    owner_list.append(owner)


data = {
    "Job Name": pipeline_names,
    "Total Runs": total_runs_list,
    "Success %": total_success_list,
    "Failures": total_failed_list,
    "Avg Duration (min)": avg_duration_list,
    "Owner/Team": owner_list,
    "Manual Triggers": manual_triggers_list,
    "Run Date": run_dates
}

df = pd.DataFrame(data)
# -----------------------------
# Streamlit Layout
# -----------------------------
st.write(f"Date and Time: {current_time}")
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
# st.dataframe(filtered_df.groupby("Job Name").agg({
#     "Total Runs": "sum",
#     "Success %": "mean",
#     "Failures": "sum",
#     "Avg Duration (min)": "mean",
#     "Owner/Team": "first",
#     "Manual Triggers": "sum"
# }).sort_values(by="Failures", ascending=False).style.background_gradient(subset=["Success %"], cmap="Greens"))

# Aggregate
summary_df = filtered_df.groupby("Job Name").agg({
    "Total Runs": "sum",
    "Success %": "mean",
    "Failures": "sum",
    "Avg Duration (min)": "mean",
    "Owner/Team": "first",
    "Manual Triggers": "sum"
}).reset_index()

# Round Success % and Avg Duration
summary_df["Success %"] = summary_df["Success %"].map("{:.2f}".format)
summary_df["Avg Duration (min)"] = summary_df["Avg Duration (min)"].map("{:.2f}".format)


# Display with background gradient
st.dataframe(
    summary_df.sort_values(by="Failures", ascending=False)
               .reset_index(drop=True)
              .style.background_gradient(subset=["Success %"], cmap="Greens")
              .set_properties(**{"text-align": "center"})
)

# -----------------------------
# Charts & Trends
# -----------------------------
st.header("Charts & Trends")

# Success vs Failures
df_chart = filtered_df.groupby("Job Name").agg({"Success %": "mean", "Failures": "sum"}).reset_index()
df_chart_melt = df_chart.melt(id_vars="Job Name", var_name="Metric", value_name="Value")
# Set custom colors
color_map = {
    "Success %": "green",   # color for success
    "Failures": "red"       # color for failures
}
fig1 = px.bar(df_chart_melt, x="Job Name", y="Value", color="Metric",color_discrete_map=color_map,barmode="group",
              title="Job Success % vs Failures", height=400)
st.plotly_chart(fig1, width='stretch')

# Average Duration Chart
fig2 = px.bar(filtered_df.groupby("Job Name")["Avg Duration (min)"].mean().reset_index(),
              x="Job Name", y="Avg Duration (min)", color="Avg Duration (min)",
              title="Average Job Duration (min)", height=400)
st.plotly_chart(fig2, width='stretch')

# Failures Heatmap

failures_sum = filtered_df.groupby("Job Name")["Failures"].sum().to_frame().T
fig3 = px.imshow(failures_sum, text_auto=True,
                 labels=dict(x="Job Name", y="Metric", color="Failures"),
                 x=failures_sum.columns, y=["Failures"], title="Failures Heatmap")
st.plotly_chart(fig3, width='stretch')

# Convert Success % back to float (since you formatted it as string earlier)
summary_df["Success %"] = summary_df["Success %"].astype(float)

# Total runs and failures
total_runs = summary_df["Total Runs"].sum()
total_failures = summary_df["Failures"].sum()

# Compute total successes
total_success = total_runs - total_failures

# Pie chart with higher DPI
pie_fig, ax = plt.subplots(figsize=(4, 4), dpi=150)  # bigger and higher DPI
ax.pie(
    [total_success, total_failures],
    labels=[f"Success ({total_success})", f"Fail ({total_failures})"],
    autopct="%1.1f%%",
    colors=["#4CAF50", "#F44336"],
    startangle=90,
    textprops={'fontsize': 6}  # adjust label text size
)

st.header("Overall Pipeline Success vs Fail")
# Make it fit nicely in Streamlit
st.pyplot(pie_fig, use_container_width=True)


# -----------------------------
# Team Filter
# -----------------------------
team_filter = st.sidebar.multiselect("Select Team", options=df["Owner/Team"].unique(), default=df["Owner/Team"].unique())
final_df = filtered_df[filtered_df["Owner/Team"].isin(team_filter)]
final_df["Success %"] = final_df["Success %"].map("{:.2f}".format)
final_df["Avg Duration (min)"] = final_df["Avg Duration (min)"].map("{:.2f}".format)
final_df = final_df.drop(columns=["Run Date"])
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