import pandas as pd
from db_connection import engine

def load_data():

    query = "SELECT * FROM pipeline_runs"
    df = pd.read_sql(query, engine)

    df["run_date"] = pd.to_datetime(df["run_date"])

    return df


def pipeline_reliability(df):

    total = df.groupby("pipeline_name").size()
    success = df[df["status"] == "success"].groupby("pipeline_name").size()

    reliability = (success / total * 100).fillna(0)

    return reliability.reset_index(name="reliability_score")


def yearly_report(df):

    df["year"] = df["run_date"].dt.year

    return (
        df.groupby(["year","status"])
        .size()
        .reset_index(name="count")
    )