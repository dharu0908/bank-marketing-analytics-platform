from airflow import DAG
from airflow.providers.databricks.operators.databricks import DatabricksRunNowOperator
from airflow.operators.email import EmailOperator
from datetime import datetime, timedelta

# ─── DEFAULT SETTINGS ────────────────────────────────────────────────────────
default_args = {
    "owner"           : "data_engineering_team",
    "retries"         : 2,
    "retry_delay"     : timedelta(minutes=5),
    "email_on_failure": True,
    "email"           : ["dataengineer@bank.com"],
    "start_date"      : datetime(2025, 1, 1)
}

# ─── DAG DEFINITION ──────────────────────────────────────────────────────────
with DAG(
    dag_id="bank_telemarketing_pipeline",
    default_args=default_args,
    description="End to end bank telemarketing analytics pipeline",
    schedule_interval="0 6 1 * *",  # runs monthly on 1st at 6am
    catchup=False,
    tags=["bank", "telemarketing", "pyspark"]
) as dag:

    # ─── TASK 1 — SILVER CLEANING ─────────────────────────────────────────
    silver_cleaning = DatabricksRunNowOperator(
        task_id="01_silver_cleaning",
        databricks_conn_id="databricks_default",
        job_id=1001,  # replace with your actual Databricks job ID
        notebook_params={"env": "production"}
    )

    # ─── TASK 2 — EDA ─────────────────────────────────────────────────────
    eda = DatabricksRunNowOperator(
        task_id="02_eda",
        databricks_conn_id="databricks_default",
        job_id=1002,  # replace with your actual Databricks job ID
        notebook_params={"env": "production"}
    )

    # ─── TASK 3 — FEATURE ENGINEERING ────────────────────────────────────
    feature_engineering = DatabricksRunNowOperator(
        task_id="03_feature_engineering",
        databricks_conn_id="databricks_default",
        job_id=1003,  # replace with your actual Databricks job ID
        notebook_params={"env": "production"}
    )

    # ─── TASK 4 — ML TRAINING ────────────────────────────────────────────
    ml_training = DatabricksRunNowOperator(
        task_id="04_ml_training",
        databricks_conn_id="databricks_default",
        job_id=1004,  # replace with your actual Databricks job ID
        notebook_params={"env": "production"}
    )

    # ─── TASK 5 — CLUSTERING ─────────────────────────────────────────────
    clustering = DatabricksRunNowOperator(
        task_id="05_clustering",
        databricks_conn_id="databricks_default",
        job_id=1005,  # replace with your actual Databricks job ID
        notebook_params={"env": "production"}
    )

    # ─── TASK 6 — SUCCESS NOTIFICATION ───────────────────────────────────
    success_notification = EmailOperator(
        task_id="06_success_notification",
        to="marketing_team@bank.com",
        subject="Bank Telemarketing Pipeline Complete",
        html_content="""
            <h3>Pipeline completed successfully</h3>
            <p>All tables updated:</p>
            <ul>
                <li>bank_silver — cleaned data</li>
                <li>bank_gold — feature engineered data</li>
                <li>bank_dim_customer — with cluster labels</li>
                <li>bank_fact_marketing — with predictions</li>
            </ul>
            <p>Power BI dashboard is now refreshed.</p>
        """
    )

    # ─── TASK ORDER ───────────────────────────────────────────────────────
    silver_cleaning >> eda >> feature_engineering >> ml_training >> clustering >> success_notification
```

---

**What each part does:**
```
default_args        → retry twice if fails, email on failure
schedule_interval   → runs monthly on 1st at 6am
DatabricksRunNowOperator → triggers each notebook as a job
>>                  → defines the order of execution
success_notification → emails marketing team when done
```

---

**What to write in your README about this:**
```
In production this DAG would:
→ Trigger monthly when new campaign data arrives
→ Run all 5 notebooks in sequence automatically
→ Retry failed tasks twice before alerting
→ Email the marketing team when dashboard is ready
