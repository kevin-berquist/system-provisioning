from app import create_app

def test_ready_systems_query_stub():
    app = create_app()
    # by default, without CONTROL_DB_CONNECTION, stub returns list
    from app.db import get_ready_systems
    rows = get_ready_systems(app.config.get('CONTROL_DB_CONNECTION'))
    assert isinstance(rows, list)
    assert len(rows) >= 0
