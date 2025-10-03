import json
from app import create_app

def test_file_writer(tmp_path):
    q = tmp_path / 'queue'
    q.mkdir()
    app = create_app()
    app.config['QUEUE_FOLDER'] = str(q)
    client = app.test_client()
    payload = { 'NewShoWareControlName': 'X', 'DatabaseName': 'db', 'NewWebSiteDomain': 'qa.x.showare.net' }
    resp = client.post('/api/jobs/dev', json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    fn = q / data['filename']
    with open(fn, 'r') as f:
        j = json.load(f)
    assert j['NewShoWareControlName'] == 'X'
