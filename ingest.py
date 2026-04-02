import pandas as pd
from db_connection import engine

def ingest_file(filepath):
    print(filepath)
    columns_to_ingest = [
        "Timestamp",
        "Platform",
        "Pipeline Name",
        "Table Name",
        "Pipeline Type",
        "Source System",
        "Source Layer",
        "Target Layer",
        "Run Type",
        "Schedule",
        "Duration",
        "Status",
        "Owner"
    ]
    if filepath.endswith(".csv"):
        df = pd.read_csv(filepath, usecols=columns_to_ingest)
        print(df.head())
        num_headers = len(df.columns)

        print(f"Number of columns in CSV: {num_headers}")
        print("Column names:", df.columns.tolist())

    elif filepath.endswith(".xlsx"):
        df = pd.read_excel(filepath)

    else:
        raise ValueError("Unsupported file")

    df = df.rename(columns={
        "Timestamp": "run_date",
        "Platform": "platform",
        "Pipeline Name": "pipeline_name",
        "Table Name": "table_name",
        "Pipeline Type": "pipeline_type",
        "Source System": "source_system",
        "Source Layer": "source_layer",
        "Target Layer": "target_layer",
        "Run Type": "run_type",
        "Schedule": "schedule",
        "Duration": "duration",
        "Status": "status",
        "Owner":"owner"
        # The rest keep original names: Platform, Schedule, Duration, Status, Owner
    })
    df["run_date"] = pd.to_datetime(df["run_date"])
    # df["duration_seconds"] = pd.to_timedelta(df["Duration"]).dt.total_seconds().astype(int)
    df["duration_seconds"] = (
        pd.to_timedelta(df["duration"], errors="coerce")
        .dt.total_seconds()
    )
    df["duration_seconds"] = df["duration_seconds"].fillna(0).astype(int)
    
    df.to_sql(
        "pipeline_runs",
        engine,
        if_exists="append",
        index=False
    )

    print("File inserted successfully")