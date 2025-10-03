from backend.app import create_app
from pathlib import Path
import json

app = create_app()
client = app.test_client()

payload = {
    'DatabaseName': 'SmokeDB',
    'GeminiProjID': '9999',
    'WebServerCluster': 'us-c1webx',
    'NewDatabaseServer': 'us-clusdb1',
    'CurrentDevWebSiteDomain': 'dev.smoke.local'
}
resp = client.post('/api/jobs/prod', json=payload)
print('status', resp.status_code)
try:
    print('json', resp.get_json())
except Exception:
    print('no json')

q = Path(app.config['QUEUE_FOLDER'])
files = sorted(q.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)
if files:
    print('latest file:', files[0])
    print(files[0].read_text(encoding='utf-8'))
else:
    print('no files found in', q)
