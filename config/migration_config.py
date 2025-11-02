# config/migration_config.py
SRC_CONN_ID = "SOURCE_DB"
DST_CONN_ID = "DESTINATION_DB"

TABLES = {    
    "stg_supplier": "public.supplier_flat_tbl",   
    "stg_marketer": "public.marketer_flat_tbl"   
}

# Per-table primary key / unique constraint names used by ON CONFLICT ON CONSTRAINT <name>
CONSTRAINTS = {    
    "stg_supplier": "uq_sup_cam_line_lead_version",    
    "stg_marketer": "uq_cam_line_lead_version"    
}

NOTIFICATION_EMAILS = ["yogesh.lohar@digitalzone.com"]

DEFAULT_BATCH_SIZE = 10000
DEFAULT_PAGE_SIZE = 1000