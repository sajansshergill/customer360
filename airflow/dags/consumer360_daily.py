"""Master DAG: runs the full daily pipeline (ingest -> build -> quality -> activation).
The per-source DAGs below it exist so a single source can be re-run/backfilled alone."""
from datetime import datetime
try:
    from airflow import DAG
    from airflow.operators.bash import BashOperator
except ImportError:
    DAG = None
if DAG:
    with DAG("consumer360_daily", start_date=datetime(2025,1,1), schedule="0 6 * * *", catchup=False) as dag:
        BashOperator(task_id="run_pipeline", bash_command="bash scripts/run_pipeline.sh")
        BashOperator(task_id="data_quality", bash_command="python data_quality/run_checks.py")
