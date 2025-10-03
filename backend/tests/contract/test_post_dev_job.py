import os
import json
import tempfile
from app import create_app

def test_post_dev_job_writes_file(tmp_path, monkeypatch):
    q = tmp_path / 'queue'
    q.mkdir()
    app = create_app()
    app.config['QUEUE_FOLDER'] = str(q)
    client = app.test_client()
    payload = { 'NewShoWareControlName': 'X', 'DatabaseName': 'db', 'NewWebSiteDomain': 'qa.x.showare.net' }
    resp = client.post('/api/jobs/dev', json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'filename' in data
    fn = q / data['filename']
    assert fn.exists()
    with open(fn, 'r') as f:
        j = json.load(f)
    assert j['JobType'] == 'DEV_SETUP'
