"""Compatibility shim for tests and top-level imports.

This file exists so tests and other top-level imports can do
``from app.services import write_job_json`` while the real implementation
lives under `backend.app.services`.

Reasons for this shim (historical / practical):
- Keeps test imports short and stable (no need to manipulate PYTHONPATH
	or package structure in test runners).
- Allows the implementation to live in `backend/` where the app is
	self-contained, while exposing a small, explicit surface at the
	repository root for ease of use.

We prefer an explicit import to the previous dynamic import_module call
because it provides clearer errors, better IDE/type-checker support,
and avoids subtle import-time issues.
"""

try:
		# Import the real implementation from the backend package. This will
		# raise ImportError if the backend package is not on sys.path which
		# surfaces a clear error to the developer/test runner.
		from backend.app import services as _mod
except Exception as e:
		# Re-raise with a clearer message to aid debugging when running tests
		# or when the workspace layout is different (for example, in CI).
		raise ImportError(
				"Could not import backend.app.services. Ensure the workspace layout "
				"puts the 'backend' package on sys.path (run tests from the repo root)"
		) from e

# Export the small surface that other modules/tests expect.
make_filename = _mod.make_filename
write_job_json = _mod.write_job_json
get_ready_systems_stub = _mod.get_ready_systems_stub
