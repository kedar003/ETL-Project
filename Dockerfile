FROM python:3.12
 
WORKDIR /app
 
COPY requirements.txt /app/data_migration_tasks.txt

RUN pip install --no-cache-dir -r data_migration_tasks.txt
 
COPY . /app
CMD ["python"]
 