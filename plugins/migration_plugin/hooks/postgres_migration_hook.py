from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime
from typing import Optional

class PostgresMigrationHook(PostgresHook):
    """
    Light wrapper around Airflow's PostgresHook to expose:
     - get_last_updated_at(table)
     - export_to_csv(sql, filename)
    """

    def __init__(self, postgres_conn_id: Optional[str] = None, pool_size: int = 5, max_overflow: int = 10, *args, **kwargs):
        # allow passing postgres_conn_id name
        super().__init__(postgres_conn_id=postgres_conn_id, pool_size=pool_size, max_overflow=max_overflow, *args, **kwargs)

    def get_last_updated_at(self, table_name: str) -> datetime:
        """
        Returns max(updated_at) for the given table.
        If the column does not exist or an error occurs, returns datetime.min.
        """
        try:
            with self.get_conn() as conn, conn.cursor() as cur:
                cur.execute(f"SELECT MAX(updated_at) FROM {table_name};")
                result = cur.fetchone()
                if result and result[0] is not None:
                    return result[0]
                return datetime.min
        except Exception as e:
            # Log error if needed
            self.log.warning("Could not get last_updated_at for %s: %s", table_name, str(e))
            return datetime.min

    def export_to_csv(self, sql: str, filename: str):
        """
        Run COPY (sql) TO STDOUT WITH (FORMAT CSV, HEADER) -> write to filename
        (wraps PostgresHook.copy_expert)
        """
        copy_sql = f"COPY ({sql}) TO STDOUT WITH (FORMAT CSV, HEADER)"
        self.copy_expert(sql=copy_sql, filename=filename)
