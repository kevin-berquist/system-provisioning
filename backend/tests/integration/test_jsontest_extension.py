import json
from app import create_app

def test_jsontest_extension_write(tmp_path, monkeypatch):
    q = tmp_path / 'queue'
    q.mkdir()
    # create app and override config to use .jsontest
    app = create_app()
    app.config['QUEUE_FOLDER'] = str(q)
    app.config['JOB_FILE_EXTENSION'] = '.jsontest'
    client = app.test_client()
    payload = { 'NewShoWareControlName': 'X', 'DatabaseName': 'db', 'NewWebSiteDomain': 'qa.x.showare.net' }
    resp = client.post('/api/jobs/dev', json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'filename' in data
    filename = data['filename']
    assert filename.endswith('.jsontest')
    fn = q / filename
    with open(fn, 'r', encoding='utf-8') as f:
        j = json.load(f)
    assert j['JobType'] == 'DEV_SETUP'
