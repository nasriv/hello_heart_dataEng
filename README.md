# Hello Heart Senior Data Engineer

This is a technical assessment exam performed for 

### Setting Up Python Environment

To set up the Python environment, follow these steps:

1. **Install Python**: If you haven't already, install Python on your system. You can download it from the [official Python website](https://www.python.org/).

2. **Create a Virtual Environment**: You can create a virtual environment using `venv` or `virtualenv`:

   ```
   python -m venv .venv
   ```

3. Install depedencies
   ```
   .venv\scripts\activate
   pip install -r requirements.txt
   ```

### Setting up Airflow

In order to setup the basic Airflow infrastructure, first execute the initialization service defined in the docker file by executing. This will setup the defauly user to be able to login to the webUI on docker spin up at localhost:8080

```
docker-compose up airflow-init
```

### Spin up docker-compose services and trigger DAG

To spin up the airflow services, simply execute from the CWD
```
docker-compose up -d
```

### Setting up PostgreSQL Initialization Scripts

To setup the localstack PostgresSQL backend db, execute the following script from within your local python environment

```
python db-init.py
```
