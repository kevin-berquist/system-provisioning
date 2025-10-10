import os
import json
import uuid
from datetime import datetime, timezone

def make_filename(prefix='dev', extension='.json'):
    """Return a filename with the given prefix and extension (including leading dot).

    Example: make_filename('dev', '.jsontest') -> 'dev-20251009-120000-abc123.jsontest'
    """
    ts = datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')
    short = uuid.uuid4().hex[:6]
    return f"{prefix}-{ts}-{short}{extension}"

def write_job_json(queue_folder, payload, prefix='dev', extension='.json'):
    os.makedirs(queue_folder, exist_ok=True)
    filename = make_filename(prefix, extension=extension)
    # Use a tmp suffix for atomic write operations
    tmp_path = os.path.join(queue_folder, filename + '.tmp')
    final_path = os.path.join(queue_folder, filename)
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f, indent=2)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp_path, final_path)
    return final_path

def get_existing_prod_database_names(queue_folder, running_folder):
    """Scan queue and running folders for PROD_SETUP jobs and return set of DatabaseNames.
    
    Returns a set of DatabaseName values from existing production jobs to enable 
    filtering of Ready systems to prevent duplicate production setups.
    """
    database_names = set()
    
    for folder in [queue_folder, running_folder]:
        if not folder or not os.path.exists(folder):
            continue
            
        try:
            for filename in os.listdir(folder):
                if not filename.endswith(('.json', '.jsontest')):
                    continue
                    
                file_path = os.path.join(folder, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        payload = json.load(f)
                        
                    # Check if this is a PROD_SETUP job
                    if payload.get('JobType') == 'PROD_SETUP':
                        db_name = payload.get('DatabaseName')
                        if db_name:
                            database_names.add(db_name)
                            
                except (json.JSONDecodeError, IOError, OSError):
                    # Skip malformed or unreadable files, continue scanning
                    continue
                    
        except (OSError, IOError):
            # Skip folders that can't be read, continue with other folder
            continue
            
    return database_names

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
