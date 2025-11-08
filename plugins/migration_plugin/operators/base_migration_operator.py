from airflow.models import BaseOperator
from plugins.migration_plugin.hooks.postgres_migration_hook import PostgresMigrationHook
from plugins.migration_plugin.utils.migration_utils import upsert_rows_batch
from plugins.migration_plugin.utils.schema_validator_sqlalchemy import SchemaValidator
from migration_plugin.utils import data_validation_utils as dq
from config.migration_config import SRC_CONN_ID, DST_CONN_ID,DEFAULT_PAGE_SIZE,DEFAULT_BATCH_SIZE
from datetime import datetime
import re

class BaseMigrationOperator(BaseOperator):
    """
    Base operator for Postgres-to-Postgres migrations.
    Uses regular cursors with fetchmany() for batch processing.
    Handles incremental loads using updated_at column.
    """

    def __init__(
        self,
        src_conn_id: str,
        dst_conn_id: str,
        table_name: str,
        constraint_name: str,
        conflict_cols: list,
        immutable_cols: list = None,
        batch_size: int = DEFAULT_BATCH_SIZE,
        page_size: int = DEFAULT_PAGE_SIZE,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.src_conn_id = src_conn_id or SRC_CONN_ID
        self.dst_conn_id = dst_conn_id or DST_CONN_ID
        self.table_name = table_name
        self.constraint_name = constraint_name
        self.conflict_cols = conflict_cols
        self.immutable_cols = immutable_cols or []
        self.batch_size = batch_size
        self.page_size = page_size

    def get_last_updated_at(self, dst_hook: PostgresMigrationHook):
        """
        Fetch last updated timestamp for incremental loads.
        Fallbacks to 1900-01-01 00:00:00 if table is empty or column missing.
        """
        try:
            last_updated = dst_hook.get_last_updated_at(self.table_name)
            if not last_updated:
                last_updated = datetime(1900, 1, 1)
            return last_updated
        except Exception as e:
            self.log.warning(
                "Could not get last_updated_at for %s: %s. Defaulting to full load.",
                self.table_name,
                str(e),
            )
            return datetime(1900, 1, 1)

    def fetch_source_data(self, src_hook: PostgresMigrationHook, last_updated_at):
        """
        Regular cursor generator. Fetches data in batches using fetchmany().
        Avoids server-side cursor/autocommit issues.
        """
        sql = f"SELECT * FROM {self.table_name} WHERE updated_at >= %s::timestamp"
        try:
            conn = src_hook.get_conn()
            with conn.cursor() as cur:
                cur.execute(sql, (last_updated_at,))
                if not cur.description:
                    raise RuntimeError(f"No result set returned for query on {self.table_name}")

                columns = [desc[0] for desc in cur.description]

                while True:
                    rows = cur.fetchmany(self.batch_size)
                    if not rows:
                        break
                    yield rows, columns

        except Exception as e:
            self.log.error("Error fetching data for %s: %s", self.table_name, str(e))
            return

    def execute(self, context):
        src_hook = PostgresMigrationHook(postgres_conn_id=self.src_conn_id)
        dst_hook = PostgresMigrationHook(postgres_conn_id=self.dst_conn_id)

        # Validate schema alignment
        validator = SchemaValidator(src_hook, dst_hook)
        validator.validate_table(self.table_name)

        last_updated_at = self.get_last_updated_at(dst_hook)
        self.log.info("Last updated at for %s: %s", self.table_name, last_updated_at)

        total_rows = 0
        with dst_hook.get_conn() as dst_conn:
            for batch_number, batch in enumerate(
                self.fetch_source_data(src_hook, last_updated_at), start=1
            ):
                if not batch:
                    continue
                rows, columns = batch
                total_rows += len(rows)
                self.log.info("Processing batch %d with %d rows...", batch_number, len(rows))

                upsert_rows_batch(
                    conn=dst_conn,
                    table_name=self.table_name,
                    rows=rows,
                    columns=columns,
                    conflict_cols=self.conflict_cols,
                    immutable_cols=self.immutable_cols,
                    constraint_name=self.constraint_name,
                    page_size=self.page_size,
                )

        self.log.info(
            "Migration completed for %s. Total rows processed: %d",
            self.table_name,
            total_rows,
        )

        # --- Row count validation after migration ---
        try:
            dq.validate_row_count(src_hook, dst_hook, table_name=self.table_name, last_updated_at=last_updated_at)
            self.log.info("Row count validation passed for %s", self.table_name)
        except ValueError as e:
            self.log.error("Row count validation failed: %s", str(e))
            raise
