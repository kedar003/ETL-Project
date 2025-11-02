import logging
import pandas as pd
from typing import List, Callable, Dict

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def validate_row_count(src_hook, dst_hook, table_name: str, last_updated_at: str = None) -> Dict[str, int]:
    """
    Validate that the number of rows in source and destination tables match.
    Raises ValueError if counts differ.
    """
    src_sql = f"SELECT COUNT(*) FROM {table_name}"
    dst_sql = f"SELECT COUNT(*) FROM {table_name}"

    if last_updated_at:
        src_sql += f" WHERE updated_at >= '{last_updated_at}'::timestamp"
        dst_sql += f" WHERE updated_at >= '{last_updated_at}'::timestamp"

    with src_hook.get_conn() as src_conn, dst_hook.get_conn() as dst_conn:
        with src_conn.cursor() as cur_src, dst_conn.cursor() as cur_dst:
            cur_src.execute(src_sql)
            cur_dst.execute(dst_sql)
            src_count = cur_src.fetchone()[0]
            dst_count = cur_dst.fetchone()[0]

    logger.info("Row count for table %s: source=%d, destination=%d", table_name, src_count, dst_count)

    if src_count != dst_count:
        raise ValueError(f"Row count mismatch for {table_name}: source={src_count}, destination={dst_count}")

    return {"source_count": src_count, "destination_count": dst_count}

