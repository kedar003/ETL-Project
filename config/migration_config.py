# config/migration_config.py
SRC_CONN_ID = "SOURCE_DB"
DST_CONN_ID = "DESTINATION_DB"

TABLES = {
    "campaign": "public.      campaigns",
    "lead_master": "public.      lead_master",
    "line_items": "public.      line_items",
    "line_item_status": "public.      lead_line_item_status",
    "rollup": "public.stg_lead_rollup_by_line_item"
}
# Per-table primary key / unique constraint names used by ON CONFLICT ON CONSTRAINT <name>
CONSTRAINTS = {
    "campaign": "      campaigns_pkey",
    "lead_master": "  lead_master_pkey",
    "line_items": "      line_items_pkey",
    "line_item_status": "  lead_lineitem_status_pkey",
    "rollup": "slrbli_line_item_primary_key",
}

VIEW = {    
    "stg_supplier_view": "  stage.vw_supplier_flat",   
    "stg_marketer_view": "  stage.vw_marketer_flat"   
}

NOTIFICATION_EMAILS = []

DEFAULT_BATCH_SIZE = 10000
DEFAULT_PAGE_SIZE = 1000
