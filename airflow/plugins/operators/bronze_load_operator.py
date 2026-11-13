"""Bronze load operator delegating to consumer360 ingestion loader."""
try:
    from airflow.models import BaseOperator
except ImportError:

    class BaseOperator:
        def __init__(self, task_id=None, **kw):
            self.task_id = task_id


import duckdb

from config.settings import get_settings
from consumer360.ingestion.loader import load_source_bronze


class BronzeLoadOperator(BaseOperator):
    def __init__(self, source, **kw):
        super().__init__(**kw)
        self.source = source

    def execute(self, context):
        settings = get_settings()
        con = duckdb.connect(str(settings.warehouse_path))
        try:
            n = load_source_bronze(con, settings, self.source)
        finally:
            con.close()
        return n
