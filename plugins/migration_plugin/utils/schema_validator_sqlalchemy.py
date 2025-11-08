"""
Schema Validator Utility using SQLAlchemy

This module validates that the source and destination PostgreSQL
schemas are structurally compatible before performing data migration.
"""

import re
from sqlalchemy import create_engine, inspect
from airflow.utils.log.logging_mixin import LoggingMixin


class SchemaValidator(LoggingMixin):
    def __init__(self, src_hook, dst_hook):
        super().__init__()
        self.src_hook = src_hook
        self.dst_hook = dst_hook

    # -------------------------------------------------------------------------
    # Public methods
    # -------------------------------------------------------------------------
    def validate_table(self, table_name: str):
        """Validate that source and destination tables match structurally."""
        self.log.info("Starting schema validation for table: %s", table_name)

        src_engine = self._get_sqlalchemy_engine(self.src_hook)
        dst_engine = self._get_sqlalchemy_engine(self.dst_hook)

        src_schema = self._get_table_schema(src_engine, table_name)
        dst_schema = self._get_table_schema(dst_engine, table_name)

        self.log.debug("Source schema (%s): %s", table_name, src_schema)
        self.log.debug("Destination schema (%s): %s", table_name, dst_schema)

        differences = self._compare_schemas(src_schema, dst_schema)

        if differences:
            message = self._format_differences_message(table_name, differences)
            self.log.error(message)
            raise ValueError(message)

        self.log.info("Schema validation passed for table: %s", table_name)

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    def _get_sqlalchemy_engine(self, hook):
        """Build SQLAlchemy engine from Airflow Postgres hook."""
        conn = hook.get_connection(hook.postgres_conn_id)
        uri = f"postgresql+psycopg2://{conn.login}:{conn.password}@{conn.host}:{conn.port}/{conn.schema}"
        return create_engine(uri)

    def _get_table_schema(self, engine, table_name: str):
        """Fetch column names and types for a given table using reflection."""
        inspector = inspect(engine)
        schema, _, table = table_name.partition(".")
        schema = schema or "public"

        try:
            columns = inspector.get_columns(table, schema=schema)
        except Exception as e:
            raise ValueError(f"Error inspecting table {table_name}: {e}")

        if not columns:
            raise ValueError(f"No columns found for table {table_name}")

        # Normalize type names (remove variable length, etc.)
        normalized = {
            col["name"]: self._normalize_type(str(col["type"])) for col in columns
        }
        return normalized

    def _normalize_type(self, type_str: str) -> str:
        """Normalize type string for consistent comparison (e.g., VARCHAR(255) → VARCHAR)."""
        return re.sub(r"\(.*\)", "", type_str).strip().lower()

    def _compare_schemas(self, src_schema: dict, dst_schema: dict) -> dict:
        """Compare source and destination schema dictionaries."""
        src_cols = set(src_schema.keys())
        dst_cols = set(dst_schema.keys())

        missing_in_dst = sorted(src_cols - dst_cols)
        extra_in_dst = sorted(dst_cols - src_cols)

        type_mismatches = {
            col: (src_schema[col], dst_schema[col])
            for col in src_cols & dst_cols
            if src_schema[col] != dst_schema[col]
        }

        differences = {}
        if missing_in_dst:
            differences["missing_in_destination"] = missing_in_dst
        if extra_in_dst:
            differences["extra_in_destination"] = extra_in_dst
        if type_mismatches:
            differences["type_mismatches"] = type_mismatches

        return differences

    def _format_differences_message(self, table_name: str, differences: dict) -> str:
        """Builds a readable diff message for Airflow logs."""
        lines = [f"Schema mismatch for table `{table_name}` detected:"]
        if "missing_in_destination" in differences:
            lines.append(f"   • Missing columns in destination: {differences['missing_in_destination']}")
        if "extra_in_destination" in differences:
            lines.append(f"   • Extra columns in destination: {differences['extra_in_destination']}")
        if "type_mismatches" in differences:
            mismatch_lines = [
                f"      - {col}: source={src_type}, destination={dst_type}"
                for col, (src_type, dst_type) in differences["type_mismatches"].items()
            ]
            lines.append("   • Type mismatches:\n" + "\n".join(mismatch_lines))
        return "\n".join(lines)
