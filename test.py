from pyspark.sql import SparkSession
from delta.tables import DeltaTable

spark = SparkSession.builder.getOrCreate()

# Duplicate source rows for same merge key
source_df = spark.createDataFrame([
    ("1001", "BR01", "SAP", "Johnny"),
    ("1001", "BR01", "SAP", "Jonathan")  # duplicate
], ["source_user_id", "Brand_Code", "Source_Name", "First_Name"])

delta_table = DeltaTable.forName(spark, "delta_demo_target")

delta_table.alias("target").merge(
    source_df.alias("source"),
    """
    target.source_user_id = source.source_user_id
    AND target.Brand_Code = source.Brand_Code
    AND target.Source_Name = source.Source_Name
    """
).whenMatchedUpdate(
    set={"First_Name": "source.First_Name"}
).execute()