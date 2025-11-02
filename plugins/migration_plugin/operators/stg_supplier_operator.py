from plugins.migration_plugin.operators.base_stg_migration_operator import BaseStgMigrationOperator
from migration_plugin.utils.transformers import select_stg_supplier_sql
from config.migration_config import DST_CONN_ID, TABLES, CONSTRAINTS
from migration_plugin.utils.notification_utils import notify_failure

class StgSupplierOperator(BaseStgMigrationOperator):
    def __init__(self, **kwargs):
        super().__init__(
            dst_conn_id=DST_CONN_ID,            
            target_table=TABLES["stg_supplier"],            
            constraint_name=CONSTRAINTS["stg_supplier"],
            conflict_cols=["tenant_code"],
            immutable_cols=["campaign_external_id","created_at"],
            on_failure_callback=notify_failure,
            **kwargs
        )

    def transform_sql(self, last_updated_at: str) -> str:
        return select_stg_supplier_sql(last_updated_at, table_name="public.dz_cs_campaigns")
