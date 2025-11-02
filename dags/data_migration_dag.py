# dags/data_migration_dag.py
from datetime import datetime
from airflow.decorators import dag
from migration_plugin.operators import (   
    StgSupplierOperator,
    StgMarketerOperator,    
)

@dag(dag_id="pg_to_pg_modular_migration", start_date=datetime(2024, 1, 1), schedule="*/5 * * * *", catchup=False, tags=["migration"])
def data_migration_dag():
    migrate_stg_supplier = StgSupplierOperator(task_id="migrate_stg_supplier")
    stg_marketer = StgMarketerOperator(task_id="stg_marketer")    

    # Replicates original DAG dependencies:
    # migrate_campaign() >> migrate_line_items() >> [[migrate_line_item_status() >> stg_leads(), stg_line_items()] >> stg_rollup_by_line_items(), migrate_stg_campaigns()]
    migrate_stg_supplier >> stg_marketer    

dag = data_migration_dag()
