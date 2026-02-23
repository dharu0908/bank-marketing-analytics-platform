# Bank Marketing Analytics Platform

A Portuguese bank was spending €1.2M a year on telemarketing campaigns and only converting 11% of customers. This project looks at why, finds who actually converts, and builds a pipeline to help the marketing team make better decisions.

---

## What this project does

Takes the UCI Bank Marketing dataset (45,211 customer records) and runs it through a full data engineering pipeline on Databricks. The end result is a star schema with ML-generated probability scores and customer cluster labels that the marketing team can use to prioritise who to call.

The stack is PySpark, Databricks, Delta Lake, and Apache Airflow for orchestration.

---

## The findings that actually matter

**Timing is everything.** The bank runs most of its campaigns in May which has a 6.7% conversion rate. March has a 52% conversion rate and gets almost no calls. Just shifting budget to March, September, October and December would dramatically change results without changing anything else.

**Stop calling people after 3 attempts.** Conversion drops consistently after the third call and hits near zero after six. There are 9,641 calls in this dataset made beyond the third attempt at a 7.35% conversion rate. That is roughly €252K in wasted spend annually.

**Previous success is the strongest signal.** If a customer subscribed in a previous campaign they convert at 64.7% — six times the baseline. These 1,511 customers should be the first ones called in every new campaign, not treated the same as everyone else.

**Unknown contact type is a silent budget drain.** 13,020 calls — 29% of the total — have no recorded contact method and convert at 4%. The bank is spending money on calls it isn't even tracking properly.

**Who actually subscribes:** students (28.7%), retired customers (22.8%), senior age group (18.5%), single marital status (15%), and tertiary education (15%). Blue-collar workers are the largest group called and convert at 7.4% — below half the average.

---

## ML results

Trained both Logistic Regression and Random Forest using PySpark MLlib.

| | Logistic Regression | Random Forest |
|---|---|---|
| AUC-ROC | 0.8717 | 0.8863 |
| Precision | 0.8946 | 0.8975 |
| Recall | 0.8243 | 0.8164 |
| F1 | 0.8473 | 0.8421 |

Random Forest won on AUC-ROC and Precision so that is what is used to generate the final probability scores.

The lift is significant. If you call only the top 20% of customers ranked by predicted probability you get a 33% conversion rate instead of 11%, and capture 74% of all conversions from 20% of the calls.

One honest note: call duration is the strongest feature by importance (via contact_efficiency) but it is only known after the call ends. In a real production system you would retrain without it for pre-call targeting.

---

## Customer segments (KMeans, k=6)

The elbow method pointed to 6 as the optimal number of clusters. Cost increased at k=7 so 6 was the stopping point.

| Cluster | Label | Size | Conversion |
|---|---|---|---|
| 3 | Loyal Engaged | 1,380 | 26.2% |
| 0 | Warm Prospects | 6,146 | 13.8% |
| 2 | Average Customers | 15,132 | 12.9% |
| 4 | Passive Customers | 14,671 | 10.9% |
| 1 | Over-contacted | 7,044 | 7.1% |
| 5 | Wasted Spend | 838 | 3.2% |

Cluster 3 is 100% previously contacted with an average of 8.8 prior contacts — these are warm repeat customers and should be prioritised. Cluster 5 has an average of 19 calls per customer with zero prior contact history and a 3.2% conversion rate — these should be deprioritised immediately.

---

## Data pipeline

The pipeline follows a medallion architecture on Databricks.

Raw CSV lands in the Bronze layer as a Delta table. Silver cleans it — fixes the pdays sentinel value where -1 means never contacted, caps outliers in balance and campaign, handles unknown values in job and education, and adds a log transform to balance. Gold adds engineered features and organises everything into a star schema.

```
bank_silver         cleaned and validated data
bank_gold           feature engineered
bank_dim_customer   demographics + cluster label
bank_dim_campaign   contact metrics
bank_dim_date       day, month, quarter
bank_fact_marketing conversions, cost, predicted_prob, predicted_label
```

The Airflow DAG in airflow/bank_telemarketing_dag.py orchestrates all five notebooks in sequence on a monthly schedule. In production this would trigger automatically when new campaign data arrives and email the marketing team when the pipeline completes.

---

## How to run it

You need a Databricks account. Community Edition works fine.

```
git clone https://github.com/dharu0908/bank-marketing-analytics-platform
```

Upload bank-full.csv to your Databricks DBFS at /mnt/bank/bronze/ then run the notebooks in order:

```
01_silver_cleaning.py
02_eda.py
03_feature_engineering.py
04_ml_training.py
05_clustering.py
```

For Airflow, copy airflow/bank_telemarketing_dag.py to your dags folder and update the job_id values with your actual Databricks Job IDs from Workflows.

---

## Project structure

```
bank-marketing-analytics-platform/
  notebooks/
    01_silver_cleaning.py
    02_eda.py
    03_feature_engineering.py
    04_ml_training.py
    05_clustering.py
  airflow/
    bank_telemarketing_dag.py
  README.md
```

---

Dataset from the UCI Machine Learning Repository — Bank Marketing Dataset.
