from datetime import datetime
from airflow.decorators import dag
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
# import your custom migration operators
from plugins.migration_plugin.operators import (
    CampaignMigrationOperator,
    LineItemsMigrationOperator,
    LeadMasterMigrationOperator,
    LineItemStatusOperator,
)

@dag(
    dag_id="pg_to_pg_single_migration_orchestrator",
    start_date=datetime(2024, 1, 1),
    schedule="*/5 * * * *",  # run every 5 minutes
    catchup=False,
    tags=["migration", "orchestrator"],
)
def data_migration_dag():
    # optional visual start/end anchors
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(task_id="end")

    # ---------------- MIGRATION GROUP ----------------
    with TaskGroup("migration") as migration:
        migrate_campaign = CampaignMigrationOperator(task_id="migrate_campaign")
        migrate_line_items = LineItemsMigrationOperator(task_id="migrate_line_items")
        migrate_lead_master = LeadMasterMigrationOperator(task_id="migrate_lead_master")
        migrate_line_item_status = LineItemStatusOperator(task_id="migrate_line_item_status")

        # internal dependencies (if needed)
        migrate_campaign >> migrate_line_items >> migrate_line_item_status
        migrate_lead_master  # independent task

    # ---------------- DAG ORCHESTRATION ----------------
    start >> migration >> end


dag = data_migration_dag()
