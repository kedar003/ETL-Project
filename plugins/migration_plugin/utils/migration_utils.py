from typing import List, Sequence
from psycopg2.extras import execute_values
import logging


def upsert_rows_batch(
    conn,
    table_name: str,
    rows: Sequence[Sequence],
    columns: List[str],
    conflict_cols: List[str],
    immutable_cols: List[str],
    constraint_name: str,
    page_size: int = 1000,
    retries: int = 3,
):
    """
    Perform batched UPSERT directly from rows (no Pandas).

    Args:
        conn: psycopg2 connection
        table_name: Target table name
        rows: Iterable of row tuples
        columns: List of column names (order matters)
        conflict_cols: Columns used in ON CONFLICT
        immutable_cols: Columns that must not be updated
        constraint_name: ON CONFLICT constraint name
        page_size: Batch insert size
        retries: Number of retries for transient failures
    """
    if not rows:
        return

    update_cols = [c for c in columns if c not in set(conflict_cols + immutable_cols)]
    insert_cols_sql = ",".join(columns)

    # Build UPSERT SQL dynamically
    update_set_sql = ",".join([f"{c} = EXCLUDED.{c}" for c in update_cols])
    if "updated_at" in columns and "updated_at" not in update_cols:
        update_set_sql += ("," if update_set_sql else "") + "updated_at = NOW()"

    sql = f"""
        INSERT INTO {table_name} ({insert_cols_sql})
        VALUES %s
        ON CONFLICT ON CONSTRAINT {constraint_name}
        DO UPDATE SET {update_set_sql}
    """

    for attempt in range(retries):
        try:
            with conn.cursor() as cur:
                execute_values(cur, sql, rows, page_size=page_size)
                conn.commit()
            break  # Exit loop if successful
        except (Exception) as e:
            conn.rollback()  # Rollback on failure
            if attempt < retries - 1:
                print(f"Retrying due to error: {e}")  # Log the error
            else:
                raise  # Re-raise the last exception after retries
