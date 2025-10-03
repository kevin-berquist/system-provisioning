import sys, json
from pathlib import Path
sys.path.insert(0, str(Path('.').resolve()))
from app import create_app
# run the three contract style tests manually
q = Path('tmp_queue')
if q.exists():
    import shutil
    shutil.rmtree(q)
q.mkdir()
app = create_app()
app.config['QUEUE_FOLDER'] = str(q)
client = app.test_client()

print('Running test 1: writes file')
payload = { 'DatabaseName': 'sampledb', 'GeminiProjID': 1979, 'CurrentDevWebSiteDomain': 'qa-sample.showare.net', 'NewWebSiteDomain': 'sample.showare.com' }
r = client.post('/api/jobs/prod', json=payload)
print('status', r.status_code)
print('resp', r.get_json())

print('Running test 2: derives domain')
q2 = Path('tmp_queue2')
if q2.exists():
    import shutil
    shutil.rmtree(q2)
q2.mkdir()
app2 = create_app()
app2.config['QUEUE_FOLDER'] = str(q2)
client2 = app2.test_client()
payload2 = { 'DatabaseName': 'sampledb', 'GeminiProjID': 1979, 'CurrentDevWebSiteDomain': 'qa-derived.showare.net' }
r2 = client2.post('/api/jobs/prod', json=payload2)
print('status', r2.status_code)
print('resp', r2.get_json())
with open(q2 / r2.get_json()['filename'], 'r') as f:
    j = json.load(f)
print('NewWebSiteDomain in file:', j.get('NewWebSiteDomain'))

print('Running test 3: includes ShoWareControl')
q3 = Path('tmp_queue3')
if q3.exists():
    import shutil
    shutil.rmtree(q3)
q3.mkdir()
app3 = create_app()
app3.config['QUEUE_FOLDER'] = str(q3)
client3 = app3.test_client()
payload3 = { 'DatabaseName': 'sampledb', 'GeminiProjID': 1979, 'CurrentDevWebSiteDomain': 'qa-sample.showare.net', 'ShoWareControl': 'SampleControl' }
r3 = client3.post('/api/jobs/prod', json=payload3)
print('status', r3.status_code)
print('resp', r3.get_json())
with open(q3 / r3.get_json()['filename'], 'r') as f:
    j3 = json.load(f)
print('ShoWareControl in file:', j3.get('ShoWareControl'))
