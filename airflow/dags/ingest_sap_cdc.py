"""Airflow DAG: scheduled extract -> validate -> load for its source."""
from datetime import datetime

try:
    from airflow import DAG
    from airflow.operators.python import PythonOperator
except ImportError:
    DAG = None

from config.settings import get_settings
from consumer360.connectors.sap_cdc import SAPCDCConnector


def extract(**_):
    rows = SAPCDCConnector(get_settings().data_dir).extract()
    print(len(rows), "rows")
    return len(rows)


if DAG:
    with DAG(
        "ingest_sap_cdc",
        start_date=datetime(2025, 1, 1),
        schedule="0 1 * * *",
        catchup=False,
    ) as dag:
        PythonOperator(task_id="extract_validate_load", python_callable=extract)
