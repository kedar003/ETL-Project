# config/migration_config.py
SRC_CONN_ID = "SOURCE_DB"
DST_CONN_ID = "DESTINATION_DB"

TABLES = {    
    "stg_supplier": "staging.supplier_flat_tbl",   
    "stg_marketer": "staging.marketer_flat_tbl"   
}

# Per-table primary key / unique constraint names used by ON CONFLICT ON CONSTRAINT <name>
CONSTRAINTS = {    
    "stg_supplier": "uq_sup_cam_line_lead_version",    
    "stg_marketer": "uq_cam_line_lead_version"    
}

VIEW = {    
    "stg_supplier_view": "staging.vw_supplier_flat",   
    "stg_marketer_view": "staging.vw_marketer_flat"   
}

NOTIFICATION_EMAILS = ["yogesh.lohar@digitalzone.com"]

DEFAULT_BATCH_SIZE = 10000
DEFAULT_PAGE_SIZE = 1000