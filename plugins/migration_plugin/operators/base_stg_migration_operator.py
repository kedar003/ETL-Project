from airflow.models import BaseOperator
from plugins.migration_plugin.hooks.postgres_migration_hook import PostgresMigrationHook
from plugins.migration_plugin.utils.migration_utils import upsert_rows_batch
from datetime import datetime
import re

class BaseStgMigrationOperator(BaseOperator):
    """
    Base operator for building STG tables from source tables.
    Uses regular cursors with fetchmany() for batch processing.
    Subclasses must implement `transform_sql(last_updated_at)` method.
    """

    def __init__(
        self,
        dst_conn_id: str,        
        target_table: str,        
        constraint_name: str,
        conflict_cols: list,
        immutable_cols: list = None,
        batch_size: int = 10000,
        page_size: int = 1000,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.dst_conn_id = dst_conn_id        
        self.target_table = target_table       
        self.constraint_name = constraint_name
        self.conflict_cols = conflict_cols
        self.immutable_cols = immutable_cols or []
        self.batch_size = batch_size
        self.page_size = page_size

    def transform_sql(self, last_updated_at: datetime) -> str:
        """
        Subclasses must implement this method to provide the SQL
        that builds the STG table. Should use last_updated_at for incremental load.
        """
        raise NotImplementedError("Subclasses must implement transform_sql()")

    def get_last_updated_at(self, dst_hook: PostgresMigrationHook) -> datetime:
        """Return last updated timestamp or fallback for full load"""
        try:
            last_updated = dst_hook.get_last_updated_at(self.target_table)
            return last_updated or datetime(2024, 1, 1)
        except Exception as e:
            self.log.warning(
                "Test : Could not get last_updated_at for %s: %s. Defaulting to full load.",
                self.target_table,
                str(e),
            )
            return datetime(2024, 1, 1)

    def fetch_data_batches(self, dst_conn, sql: str):
        """Fetch rows in batches using regular cursor and fetchmany"""
        try:
            with dst_conn.cursor() as cur:
                cur.execute(sql)
                if not cur.description:
                    self.log.warning("No columns returned from SQL for %s", self.target_table)
                    return
                columns = [desc[0] for desc in cur.description]

                while True:
                    rows = cur.fetchmany(self.batch_size)
                    if not rows:
                        break
                    yield rows, columns

        except Exception as e:
            self.log.error("Error fetching data for %s: %s", self.target_table, str(e))
            return

    def execute(self, context):
        dst_hook = PostgresMigrationHook(postgres_conn_id=self.dst_conn_id)        
            
        last_updated_at = self.get_last_updated_at(dst_hook)
        self.log.info("Last updated at for %s: %s", self.target_table, last_updated_at)

        sql = self.transform_sql(last_updated_at)
        self.log.info("Executing SQL for %s", self.target_table)
        self.log.debug("STG SQL: %s", sql)

        total_rows = 0
        with dst_hook.get_conn() as dst_conn:
            for batch_number, batch in enumerate(self.fetch_data_batches(dst_conn, sql), start=1):
                if not batch:
                    continue
                rows, columns = batch
                total_rows += len(rows)
                self.log.info("Processing batch %d with %d rows...", batch_number, len(rows))

                upsert_rows_batch(
                    conn=dst_conn,
                    table_name=self.target_table,
                    rows=rows,
                    columns=columns,
                    conflict_cols=self.conflict_cols,
                    immutable_cols=self.immutable_cols,
                    constraint_name=self.constraint_name,
                    page_size=self.page_size,
                )

        self.log.info("STG migration completed for %s. Total rows: %d", self.target_table, total_rows)
