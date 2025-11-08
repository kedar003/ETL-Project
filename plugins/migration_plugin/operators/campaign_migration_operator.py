from .base_migration_operator import BaseMigrationOperator
from config.migration_config import SRC_CONN_ID, DST_CONN_ID, TABLES, CONSTRAINTS
from migration_plugin.utils.notification_utils import notify_failure

class CampaignMigrationOperator(BaseMigrationOperator):
    def __init__(self, **kwargs):
        super().__init__(
            src_conn_id=SRC_CONN_ID,
            dst_conn_id=DST_CONN_ID,
            table_name=TABLES["campaign"],
            constraint_name=CONSTRAINTS["campaign"],
            conflict_cols=["id", "tenant_code", "campaign_id"],
            immutable_cols=["id", "created_at"],
            on_failure_callback=notify_failure,
            **kwargs
        )
