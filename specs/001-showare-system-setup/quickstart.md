# Quickstart: ShoWare System Setup

Prerequisites
- Python 3.11+
- pyodbc and Microsoft ODBC Driver for SQL Server (Windows)
- A writable `queue` and `running` folder accessible to the app

Local SQL Server (optional for integration tests)
- You can run a local SQL Server container using the provided `docker-compose.yml`:

   docker-compose up -d mssql

- Example environment variable for `CONTROL_DB_CONNECTION` (ODBC):

   DRIVER={ODBC Driver 18 for SQL Server};SERVER=127.0.0.1,1433;UID=sa;PWD=Your_strong@Passw0rd;Database=master

Run locally (development)
1. Create a virtual environment and install dependencies:

   python -m venv .venv
   .\.venv\Scripts\Activate.ps1; python -m pip install -r requirements.txt

2. Configure environment variables in `.env` or the system environment:
   - QUEUE_FOLDER (path to queue folder)
   - RUNNING_FOLDER
   - CONTROL_DB_CONNECTION (ODBC connection string)
      Note: this project includes a default inline CONTROL_DB_CONNECTION in `backend/app/config.py` derived from:

         Provider=SQLOLEDB;Data Source=us-mgtdb;Initial Catalog=ShoWareControl;User Id=showareuser;Password=ticketprinting;

      The default was converted to an ODBC/pyodbc string (Driver: ODBC Driver 17 for SQL Server). This is convenient for local testing but you should set `CONTROL_DB_CONNECTION` via environment variables or a secure secrets store in non-local environments.
   - DEV_DATABASE_SERVER
   - DEV_WEBSERVER
   - DEV_SYSTEM_VERSION

3. Run the app:

   .\.venv\Scripts\Activate.ps1; python -m app

IIS Hosting (production)
- Use wfastcgi or IIS ARR to host the Flask WSGI app. See `docs/iis-deploy.md` for example web.config and PowerShell helpers.

Testing
- Run pytest for unit and integration tests (DB integration tests may require a test MS SQL instance or Dockerized SQL Server).

Seeding the test DB
- After docker-compose brings up the `mssql` service, run the seed helper to populate `TicketsystemInstallations`:

   .\scripts\seed_mssql.ps1 -ContainerName system-provisioning_mssql_1 -SaPassword Your_strong@Passw0rd

This will copy `sql/seed_ticketsysteminstallations.sql` into the container and execute it via `sqlcmd`.
