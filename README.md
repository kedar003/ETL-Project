# dzone-analytics-server - modular Airflow data migration

This repository contains an Airflow 3.x modular ETL for postgres->postgres migrations.

Structure:
- `dags/` DAG orchestration
- `plugins/migration_plugin/` custom hooks/operators/utils
- `config/` migration config and table schemas
- `tests/` unit tests

Usage (local Docker dev):
1. Build:
   docker build -t dzone-analytics-server:latest --build-arg FILE_NAME=requirements.txt .

2. Run with DB (or use docker-compose):
   docker run -p 8080:8080 -v $(pwd):/app dzone-analytics-server:latest

Airflow UI: http://localhost:8080

For local linting in VS Code make sure to install the same deps in a virtualenv and select that interpreter.
