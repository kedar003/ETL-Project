from plugins.migration_plugin.operators.base_migration_operator import BaseMigrationOperator
from config.migration_config import SRC_CONN_ID, DST_CONN_ID, TABLES, CONSTRAINTS
from migration_plugin.utils.notification_utils import notify_failure

class LeadMasterMigrationOperator(BaseMigrationOperator):
    def __init__(self, **kwargs):
        super().__init__(
            src_conn_id=SRC_CONN_ID,
            dst_conn_id=DST_CONN_ID,
            table_name=TABLES["lead_master"],
            constraint_name=CONSTRAINTS["lead_master"],
            conflict_cols=["id", "email"],
            immutable_cols=["id", "created_at"],
            on_failure_callback=notify_failure,
            **kwargs
        )