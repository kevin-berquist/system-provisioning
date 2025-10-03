import os
import json
import uuid
from datetime import datetime, timezone

def make_filename(prefix='dev'):
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    short = uuid.uuid4().hex[:6]
    return f"{prefix}-{ts}-{short}.json"

def write_job_json(queue_folder, payload, prefix='dev'):
    os.makedirs(queue_folder, exist_ok=True)
    filename = make_filename(prefix)
    tmp_path = os.path.join(queue_folder, filename + '.tmp')
    final_path = os.path.join(queue_folder, filename)
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, final_path)
    return final_path

def get_ready_systems_stub():
    # In production this will query the control DB. Return a sample row for testing.
    return [
        {
            'Name': 'Sample Show',
            'DatabaseName': 'sampledb',
            'GeminiProjID': 1979,
            'CurrentDevWebSiteDomain': 'qa-sample.showare.net'
        }
    ]
