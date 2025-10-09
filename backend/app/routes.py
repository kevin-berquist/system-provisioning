from flask import Blueprint, request, jsonify, current_app, render_template
from .services import write_job_json
from .db import get_ready_systems
import os
import json
from datetime import datetime

bp = Blueprint('routes', __name__)

@bp.route('/')
def index():
    ready = get_ready_systems(current_app.config.get('CONTROL_DB_CONNECTION'))

    def read_job_folder(folder):
        items = []
        try:
            for fn in sorted(os.listdir(folder), key=lambda p: os.path.getmtime(os.path.join(folder, p)), reverse=True):
                full = os.path.join(folder, fn)
                try:
                    with open(full, 'r', encoding='utf-8') as f:
                        payload = json.load(f)
                except Exception:
                    payload = {}
                items.append({
                    'filename': fn,
                    'timestamp': datetime.fromtimestamp(os.path.getmtime(full)).isoformat(),
                    # Prefer ShoWareControl (prod payload) then NewShoWareControlName or Name
                    'name': payload.get('ShoWareControl') or payload.get('NewShoWareControlName') or payload.get('Name') or '(missing metadata)',
                    'database': payload.get('DatabaseName') or '(missing)',
                    'dev_site': payload.get('CurrentDevWebSiteDomain') or payload.get('NewWebSiteDomain') or '(missing)'
                })
        except Exception:
            # folder missing or unreadable: return empty list
            return []
        return items

    queued = read_job_folder(current_app.config.get('QUEUE_FOLDER'))
    running = read_job_folder(current_app.config.get('RUNNING_FOLDER'))

    # Prod options from config
    prod_clusters = []
    prod_dbservers = []
    try:
        prod_clusters = [s.strip() for s in current_app.config.get('PROD_WEBSERVER_CLUSTER_OPTIONS', '').split(',') if s.strip()]
    except Exception:
        prod_clusters = []
    try:
        prod_dbservers = [s.strip() for s in current_app.config.get('PROD_DATABASE_SERVER_OPTIONS', '').split(',') if s.strip()]
    except Exception:
        prod_dbservers = []

    return render_template(
        'index.html', ready=ready, queued=queued, running=running,
        prod_clusters=prod_clusters, prod_dbservers=prod_dbservers
    )

@bp.route('/api/jobs/dev', methods=['POST'])
def post_dev_job():
    data = request.get_json() or {}
    # minimal validation
    required = ['NewShoWareControlName', 'DatabaseName', 'NewWebSiteDomain']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'error': 'missing fields', 'fields': missing}), 400

    payload = {
        'JobType': 'DEV_SETUP',
        'NewShoWareControlName': data['NewShoWareControlName'],
        'DatabaseName': data['DatabaseName'],
        'DatabaseServer': current_app.config.get('DEV_DATABASE_SERVER'),
        'WebServer': current_app.config.get('DEV_WEBSERVER'),
        'NewWebSiteDomain': data['NewWebSiteDomain'],
        'NewSystemVersion': current_app.config.get('DEV_SYSTEM_VERSION'),
        'GeminiTaskID': data.get('GeminiTaskID', '000000')
    }
    # honor configured job file extension (default: .json; dev/test may set .jsontest)
    ext = current_app.config.get('JOB_FILE_EXTENSION', '.json')
    path = write_job_json(current_app.config.get('QUEUE_FOLDER'), payload, prefix='dev', extension=ext)
    return jsonify({'filename': path.split('\\')[-1], 'path': path}), 201

@bp.route('/api/jobs/prod', methods=['POST'])
def post_prod_job():
    data = request.get_json() or {}
    # Production modal should not ask for NewShoWareControlName or NewWebSiteDomain
    required = ['DatabaseName', 'GeminiProjID']
    missing = [f for f in required if not data.get(f)]
    if missing:
        return jsonify({'error': 'missing fields', 'fields': missing}), 400
    # Derive NewWebSiteDomain from the selected Ready row's CurrentDevWebSiteDomain unless explicitly provided
    new_site = data.get('NewWebSiteDomain') or data.get('CurrentDevWebSiteDomain') or ''
    payload = {
        'JobType': 'PROD_SETUP',
        'WebServerCluster': data.get('WebServerCluster', current_app.config.get('PROD_WEBSERVER_CLUSTER_OPTIONS').split(',')[0]),
        'NewDatabaseServer': data.get('NewDatabaseServer', current_app.config.get('PROD_DATABASE_SERVER_OPTIONS').split(',')[0]),
        'DatabaseName': data['DatabaseName'],
        # include ShoWareControl derived from the ready row name if present
        'ShoWareControl': data.get('ShoWareControl') or data.get('Name') or data.get('CurrentDevWebSiteDomain'),
        'CurrentDevWebSiteDomain': data.get('CurrentDevWebSiteDomain'),
        'NewWebSiteDomain': new_site,
        'Version': current_app.config.get('PROD_VERSION'),
        'GeminiProjID': data['GeminiProjID']
    }
    ext = current_app.config.get('JOB_FILE_EXTENSION', '.json')
    path = write_job_json(current_app.config.get('QUEUE_FOLDER'), payload, prefix='prod', extension=ext)
    return jsonify({'filename': path.split('\\')[-1], 'path': path}), 201
