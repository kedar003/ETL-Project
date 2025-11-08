from plugins.migration_plugin.operators.base_migration_operator import BaseMigrationOperator
from config.migration_config import SRC_CONN_ID, DST_CONN_ID, TABLES, CONSTRAINTS
from plugins.migration_plugin.utils.notification_utils import notify_failure

class LineItemStatusOperator(BaseMigrationOperator):
    def __init__(self, **kwargs):
        super().__init__(
            src_conn_id=SRC_CONN_ID,
            dst_conn_id=DST_CONN_ID,
            table_name=TABLES["line_item_status"],
            constraint_name=CONSTRAINTS["line_item_status"],
            conflict_cols=["tenant_code", "lineitem_id", "tracking_id"],
            immutable_cols=["id", "created_at"],
            on_failure_callback=notify_failure,
            **kwargs
        )
