import json
from app import create_app

def test_post_prod_job_writes_file(tmp_path):
    q = tmp_path / 'queue'
    q.mkdir()
    app = create_app()
    app.config['QUEUE_FOLDER'] = str(q)
    client = app.test_client()
    payload = { 'DatabaseName': 'sampledb', 'GeminiProjID': 1979, 'CurrentDevWebSiteDomain': 'qa-sample.showare.net', 'NewWebSiteDomain': 'sample.showare.com' }
    resp = client.post('/api/jobs/prod', json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'filename' in data
    fn = q / data['filename']
    assert fn.exists()
    with open(fn, 'r') as f:
        j = json.load(f)
    assert j['JobType'] == 'PROD_SETUP'


def test_post_prod_job_derives_domain_when_missing(tmp_path):
    q = tmp_path / 'queue'
    q.mkdir()
    app = create_app()
    app.config['QUEUE_FOLDER'] = str(q)
    client = app.test_client()
    # omit NewWebSiteDomain; provide CurrentDevWebSiteDomain which should be used as NewWebSiteDomain
    payload = { 'DatabaseName': 'sampledb', 'GeminiProjID': 1979, 'CurrentDevWebSiteDomain': 'qa-derived.showare.net' }
    resp = client.post('/api/jobs/prod', json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    fn = q / data['filename']
    assert fn.exists()
    with open(fn, 'r') as f:
        j = json.load(f)
    # NewWebSiteDomain should be derived from CurrentDevWebSiteDomain when omitted
    assert j['NewWebSiteDomain'] == 'qa-derived.showare.net'


def test_post_prod_job_includes_showarecontrol_when_provided(tmp_path):
    q = tmp_path / 'queue'
    q.mkdir()
    app = create_app()
    app.config['QUEUE_FOLDER'] = str(q)
    client = app.test_client()
    # provide ShoWareControl (as the UI will include it from the ready row)
    payload = { 'DatabaseName': 'sampledb', 'GeminiProjID': 1979, 'CurrentDevWebSiteDomain': 'qa-sample.showare.net', 'ShoWareControl': 'SampleControl' }
    resp = client.post('/api/jobs/prod', json=payload)
    assert resp.status_code == 201
    data = resp.get_json()
    fn = q / data['filename']
    assert fn.exists()
    with open(fn, 'r') as f:
        j = json.load(f)
    # ShoWareControl should be present and equal to provided value
    assert j.get('ShoWareControl') == 'SampleControl'
