import os
import logging

def get_ready_systems(connection_string=None):
    """Return list of ready systems from the control DB.

    If connection_string is not provided or pyodbc is unavailable, falls back
    to a sample stub for local development.
    """
    if not connection_string:
        from .services import get_ready_systems_stub
        return get_ready_systems_stub()

    try:
        import pyodbc
    except Exception:
        logging.exception('pyodbc not available; returning stub data')
        from .services import get_ready_systems_stub
        return get_ready_systems_stub()

    conn = None
    try:
        conn = pyodbc.connect(connection_string, timeout=5)
        cursor = conn.cursor()
        # NOTE: The control DB `Name` column is the canonical ShoWare control identifier
        # used by the operations UI and by produced PROD_SETUP JSON as `ShoWareControl`.
        # We select it here as `Name` and later map it into job payloads.
        query = (
            "SELECT Name, DatabaseName, GeminiProjectID AS GeminiProjID, DirPathDev AS CurrentDevWebSiteDomain "
            "FROM TicketsystemInstallations "
            "WHERE GeminiProjectID <> 0 AND DevSystemSetup > GETDATE() - 180 AND DeploymentCountry = 2 AND LIVE=0"
        )
        rows = []
        for r in cursor.execute(query):
            rows.append({
                'Name': getattr(r, 'Name', None),
                'DatabaseName': getattr(r, 'DatabaseName', None),
                'GeminiProjID': getattr(r, 'GeminiProjID', None),
                'CurrentDevWebSiteDomain': getattr(r, 'CurrentDevWebSiteDomain', None)
            })
        cursor.close()
        return rows
    except Exception:
        logging.exception('Error querying control DB; returning stub data')
        from .services import get_ready_systems_stub
        return get_ready_systems_stub()
    finally:
        if conn:
            try:
                conn.close()
            except Exception:
                pass
