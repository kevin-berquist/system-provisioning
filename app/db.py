from importlib import import_module

_mod = import_module('backend.app.db')

get_ready_systems = getattr(_mod, 'get_ready_systems')
