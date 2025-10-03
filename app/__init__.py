"""Compatibility shim package so tests can import `app` while implementation lives in backend/app
"""
from importlib import import_module

_backend_app = import_module('backend.app')

# re-export create_app
create_app = getattr(_backend_app, 'create_app')

# try to expose submodules for convenience
try:
    services = import_module('backend.app.services')
except Exception:
    services = None
try:
    db = import_module('backend.app.db')
except Exception:
    db = None
try:
    config = import_module('backend.app.config')
except Exception:
    config = None

__all__ = ['create_app', 'services', 'db', 'config']
