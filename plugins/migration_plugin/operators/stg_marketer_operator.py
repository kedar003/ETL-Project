from plugins.migration_plugin.operators.base_stg_migration_operator import BaseStgMigrationOperator
from plugins.migration_plugin.utils.transformers import select_stg_marketer_sql
from config.migration_config import DST_CONN_ID, TABLES, CONSTRAINTS, VIEW
from plugins.migration_plugin.utils.notification_utils import notify_failure

class StgMarketerOperator(BaseStgMigrationOperator):
    def __init__(self, **kwargs):
        super().__init__(
            dst_conn_id=DST_CONN_ID,            
            target_table=TABLES["stg_marketer"],            
            constraint_name=CONSTRAINTS["stg_marketer"],
            conflict_cols=["tenant_code"],
            immutable_cols=["campaign_external_id","created_at"],
            on_failure_callback=notify_failure,
            **kwargs
        )

    def transform_sql(self, last_updated_at: str) -> str:
        return select_stg_marketer_sql(last_updated_at, table_name=VIEW["stg_marketer_view"])    
    
