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

3. Run the app (development server):

   .\.venv\Scripts\Activate.ps1; python -m backend.run

Production (Waitress behind IIS)
- The project targets Windows Server / IIS hosting. For production deployments we recommend running the Flask app with the Waitress WSGI server and wiring IIS to it using HttpPlatformHandler (or similar process manager). This keeps the app process separate from IIS while allowing IIS to proxy and manage the process.

IIS (HttpPlatformHandler) configuration (preferred production example)

Below is a minimal `web.config` that starts Python from a virtual environment and runs Waitress directly. It uses the IIS-assigned `%HTTP_PLATFORM_PORT%` so Waitress listens on the same port IIS proxies to. Update the `processPath` and environment variable paths to match your host layout.

web.config (place in the site root):

```xml
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <httpPlatform
      processPath="C:\inetpub\wwwroot\shoare\.venv\Scripts\python.exe"
      arguments="-m waitress --port %HTTP_PLATFORM_PORT% --threads 12 --call \"backend.app:create_app\""
      stdoutLogEnabled="true"
      stdoutLogFile="C:\inetpub\logs\LogFiles\shoare-python.log"
      processesPerApplication="1">
      <environmentVariables>
        <environmentVariable name="HTTP_PLATFORM_PORT" value="%HTTP_PLATFORM_PORT%" />
        <environmentVariable name="QUEUE_FOLDER" value="C:\inetpub\wwwroot\shoare\data\queue" />
        <environmentVariable name="RUNNING_FOLDER" value="C:\inetpub\wwwroot\shoare\data\running" />
        <!-- Optional operational secrets/identifiers -->
        <environmentVariable name="SHOWARE_TSID" value="{some tsid}" />
        <environmentVariable name="SHOWARE_ADMIN_USER" value="{some admin user}" />
      </environmentVariables>
    </httpPlatform>
  </system.webServer>
</configuration>
```

Notes:
- `processPath` should point to the Python executable inside the virtual environment on the IIS host.
- `arguments` use `-m waitress --port %HTTP_PLATFORM_PORT% --call "backend.app:create_app"` to run the app factory. Ensure `waitress` is installed and pinned in `backend/requirements.txt`.
- The environment variables set above (QUEUE_FOLDER, RUNNING_FOLDER) will be visible to the started process and should be used by the app configuration.
- Ensure the IIS user has write permission to the log and data folders specified.

Troubleshooting:
- If IIS fails to start the process, check the stdout log path configured in `web.config` for errors and verify virtualenv paths are correct.

Testing
- Run pytest for unit and integration tests (DB integration tests may require a test MS SQL instance or Dockerized SQL Server).

Seeding the test DB
- After docker-compose brings up the `mssql` service, run the seed helper to populate `TicketsystemInstallations`:

   .\scripts\seed_mssql.ps1 -ContainerName system-provisioning_mssql_1 -SaPassword Your_strong@Passw0rd

This will copy `sql/seed_ticketsysteminstallations.sql` into the container and execute it via `sqlcmd`.
