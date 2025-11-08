# config/migration_config.py
SRC_CONN_ID = "SOURCE_DB"
DST_CONN_ID = "DESTINATION_DB"

TABLES = {
    "campaign": "public.dz_cs_campaigns",
    "lead_master": "public.dz_cs_lead_master",
    "line_items": "public.dz_cs_line_items",
    "line_item_status": "public.dz_cs_lead_line_item_status",
    "rollup": "public.stg_lead_rollup_by_line_item"
}
# Per-table primary key / unique constraint names used by ON CONFLICT ON CONSTRAINT <name>
CONSTRAINTS = {
    "campaign": "dz_cs_campaigns_pkey",
    "lead_master": "dz_lead_master_pkey",
    "line_items": "dz_cs_line_items_pkey",
    "line_item_status": "dz_lead_lineitem_status_pkey",
    "rollup": "slrbli_line_item_primary_key",
}

VIEW = {    
    "stg_supplier_view": "staging.vw_supplier_flat",   
    "stg_marketer_view": "staging.vw_marketer_flat"   
}

NOTIFICATION_EMAILS = ["yogesh.lohar@digitalzone.com"]

DEFAULT_BATCH_SIZE = 10000
DEFAULT_PAGE_SIZE = 1000