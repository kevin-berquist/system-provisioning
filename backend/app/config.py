import os

def load_config(app):
    # Load minimal required config from environment
    app.config['QUEUE_FOLDER'] = os.getenv('QUEUE_FOLDER', os.path.join(os.getcwd(), 'dev', 'queue'))
    app.config['RUNNING_FOLDER'] = os.getenv('RUNNING_FOLDER', os.path.join(os.getcwd(), 'dev', 'running'))
    # Default pyodbc connection string derived from the provided OLE DB string:
    # Provider=SQLOLEDB;Data Source=us-mgtdb;Initial Catalog=ShoWareControl;User Id=showareuser;Password=ticketprinting;
    # Converted to a pyodbc/ODBC-style connection string. Adjust DRIVER as needed on your host.
    default_conn = (
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=us-mgtdb;"
        "DATABASE=ShoWareControl;"
        "UID=showareuser;"
        "PWD=ticketprinting;"
        "TrustServerCertificate=yes;"
    )
    app.config['CONTROL_DB_CONNECTION'] = os.getenv('CONTROL_DB_CONNECTION', default_conn)
    app.config['DEV_DATABASE_SERVER'] = os.getenv('DEV_DATABASE_SERVER', 'us-devdb')
    app.config['DEV_WEBSERVER'] = os.getenv('DEV_WEBSERVER', 'us-devweb')
    app.config['DEV_SYSTEM_VERSION'] = os.getenv('DEV_SYSTEM_VERSION', '2.02.28')
    app.config['PROD_VERSION'] = os.getenv('PROD_VERSION', '2.02.28')
    app.config['PROD_WEBSERVER_CLUSTER_OPTIONS'] = os.getenv('PROD_WEBSERVER_CLUSTER_OPTIONS', 'us-c1webx,us-c2webx,au-c1webx,uk-c1webx')
    app.config['PROD_DATABASE_SERVER_OPTIONS'] = os.getenv('PROD_DATABASE_SERVER_OPTIONS', 'us-clusdb1,us-clusdb2,au-clusdb1,uk-clusdb1')
    # Optional: override the job file extension. Default is .json. For development/test deployments
    # operators may set JOB_FILE_EXTENSION to ".jsontest" to prevent external processors that only
    # match on .json from picking up files intended for manual inspection.
    app.config['JOB_FILE_EXTENSION'] = os.getenv('JOB_FILE_EXTENSION', '.json')
