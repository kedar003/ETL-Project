from airflow.utils.email import send_email
from airflow.utils.state import State
from airflow.utils.log.logging_mixin import LoggingMixin
from airflow import settings
from config.migration_config import NOTIFICATION_EMAILS
 
def notify_failure(context):
    """
    Custom on_failure_callback for Airflow tasks.
    Logs the failure and sends an email notification.
    Works with Airflow 2.7+ RuntimeTaskInstance.
    """
    log = LoggingMixin().log
    task = context.get("task")
    task_instance = context.get("task_instance")
    exception = context.get("exception")
    dag = context.get("dag")
    dag_id = dag.dag_id if dag else "unknown_dag"
    task_id = task_instance.task_id if task_instance else "unknown_task"
    execution_date = context.get("execution_date")
 
    # Compute log URL safely
    log_url = None
    try:
        if hasattr(task_instance, "log_url"):
            log_url = task_instance.log_url
        else:
            # fallback for RuntimeTaskInstance
            from airflow.utils.urls import get_ui_url_for_task_instance
            log_url = get_ui_url_for_task_instance(task_instance)
    except Exception:
        log_url = "Could not determine log URL"
 
    # --- Log in Airflow ---
    if task:
        task.log.error("Task failed: %s.%s", dag_id, task_id)
        task.log.error("Exception: %s", exception)
        task.log.error("Log URL: %s", log_url)
    else:
        log.error("Task failed: %s.%s", dag_id, task_id)
        log.error("Exception: %s", exception)
        log.error("Log URL: %s", log_url)
 
    # --- Email content ---
    subject = f"Airflow Task Failed: {dag_id}.{task_id}"
    html_content = f"""
    <h3>Airflow Task Failure Alert</h3>
    <b>DAG:</b> {dag_id}<br>
    <b>Task:</b> {task_id}<br>
    <b>Execution Time:</b> {execution_date}<br>
    <b>Log URL:</b> <a href="{log_url}">{log_url}</a><br><br>
    <b>Error:</b><pre>{exception}</pre>
    """
 
    # --- Send email ---
    try:
        send_email(
            to=NOTIFICATION_EMAILS,
            subject=subject,
            html_content=html_content,
        )
        if task:
            task.log.info("Failure notification email sent for %s.%s", dag_id, task_id)
        else:
            log.info("Failure notification email sent for %s.%s", dag_id, task_id)
    except Exception as e:
        if task:
            task.log.error("Failed to send failure email for %s.%s: %s", dag_id, task_id, e)
        else:
            log.error("Failed to send failure email for %s.%s: %s", dag_id, task_id, e)