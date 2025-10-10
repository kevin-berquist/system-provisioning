# Tasks: ShoWare System Setup

**Input**: Design documents in `C:\Users\KevinBerquist\github\system-provisioning\specs\001-showare-system-setup/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/

## Execution Flow (main)
1. Follow TDD: write failing tests (contract & integration) before implementation
2. Implement minimal features to make tests pass
3. Iterate until quickstart scenarios succeed

## Phase 3.1: Setup
- T001 Initialize project skeleton (backend/) and project metadata
  - Create `backend/` directory
  - Files: `backend/app/__init__.py`, `backend/app/routes.py`, `backend/app/services.py`, `backend/requirements.txt`, `backend/run.py`, `backend/.env.sample`
  - Purpose: scaffold Flask app, include pyodbc in `requirements.txt`
  - Path: `C:\Users\KevinBerquist\github\system-provisioning\backend`

- T002 [P] Create `queue` and `running` folders and document permissions
  - Create `dev_queue` test folder under repo for local testing: `dev/queue`, `dev/running`
  - Add README note about required write permissions for the app user
  - Path: repo root (folders)

- T003 [P] Add configuration loading and constants
  - Implement env/config loader in `backend/app/config.py` to read QUEUE_FOLDER, RUNNING_FOLDER, CONTROL_DB_CONNECTION, DEV_DATABASE_SERVER, DEV_WEBSERVER, DEV_SYSTEM_VERSION, PROD_VERSION, PROD_WEBSERVER_CLUSTER_OPTIONS, PROD_DATABASE_SERVER_OPTIONS
  - Path: `backend/app/config.py`

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE IMPLEMENTATION
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**

- T004 [P] Contract test for POST /api/jobs/dev
  - Create `backend/tests/contract/test_post_dev_job.py`
  - Test should POST minimal valid JSON (NewShoWareControlName, DatabaseName, NewWebSiteDomain) and assert 201 and returned filename path; assert file exists in QUEUE_FOLDER path when invoked against local file-writer stub.
  - Path: `C:\Users\KevinBerquist\github\system-provisioning\backend\tests\contract\test_post_dev_job.py`

- T005 [P] Contract test for POST /api/jobs/prod
  - Create `backend/tests/contract/test_post_prod_job.py`
  - Test should POST using a sample ReadySystemRow values (DatabaseName, CurrentDevWebSiteDomain, GeminiProjID) and NewWebSiteDomain and assert 201 and filename; assert JSON contains Version and JobType constants.
  - Path: `backend/tests/contract/test_post_prod_job.py`

- T006 [P] Integration test: DB query for ready systems
  - Create `backend/tests/integration/test_ready_systems_query.py`
  - Mock or use test MSSQL to validate the query returns expected columns and rows mapping to ReadySystemRow.
  - Path: `backend/tests/integration/test_ready_systems_query.py`

- T007 [P] Integration test: file writer writes JSON to QUEUE_FOLDER
  - Create `backend/tests/integration/test_file_writer.py`
  - Validate generated filename pattern and JSON schema in the written file.
  - Path: `backend/tests/integration/test_file_writer.py`

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- T008 [P] Implement config loader and constants
  - File: `backend/app/config.py` (implement per T003)
  - Ensure constants cannot be overridden by UI

- T009 Implement file writer service
  - File: `backend/app/services.py` (add FileWriter class)
  - Responsibilities: generate filename pattern, write JSON atomically (write temp -> move), validate inputs
  - Path: `backend/app/services.py`

- T010 Implement DB access service
  - File: `backend/app/db.py` (wrap pyodbc connections, parameterized queries, function `get_ready_systems()` that runs the provided SQL)
  - Path: `backend/app/db.py`

- T011 Implement API endpoint: POST /api/jobs/dev
  - File: `backend/app/routes.py` (add route to accept Dev job form/API, validate inputs, call FileWriter)
  - Path: `backend/app/routes.py`

- T012 Implement API endpoint: POST /api/jobs/prod
  - File: `backend/app/routes.py` (add route to create Prod job JSON using ReadySystemRow data and user-provided NewWebSiteDomain)
  - Path: `backend/app/routes.py`

- T013 Implement UI pages (vanilla HTML/CSS/JS)
  - Files: `backend/templates/index.html`, `backend/static/main.css`, `backend/static/main.js`
  - Pages: Main screen lists queued/running files and ready-for-production list; Create Dev Site form modal/button; Setup Production button per system
  - Modal requirements: In-page modal dialogs with inline validation, no native prompt()/alert() usage
  - UI consistency: Apply equal padding to all UI containers (tables, modals, cards, panels) per constitution
  - Path: `backend/templates/`, `backend/static/`

## Phase 3.4: Integration
- T014 Connect DB service to control DB and wire `get_ready_systems()` into the main page
  - Ensure DB errors are handled gracefully and surfaced to operators

- T015 Request/response logging and minimal observability
  - Add structured logs for file creation, DB queries, errors
  - File: `backend/app/logging.py` or integrated in `services.py`

- T016 Validate IIS packaging docs and provide run_iis.ps1
  - File: `backend/run_iis.ps1` and `docs/iis-deploy.md`

## Phase 3.5: Polish
- T017 [P] Unit tests for validation functions
  - Files: `backend/tests/unit/test_validation.py`

- T018 [P] Performance and basic load test (smoke)
  - Add basic script to simulate multiple Create Dev Site requests and inspect file writes

- T019 [P] Documentation: update quickstart.md with exact env vars and IIS steps

- T020 [P] Add CI job (optional): run unit tests and DB integration smoke tests using a test MS SQL or dockerized instance

- T021 [P] Implement configurable file extension for dev/test environments
  - Add JOB_FILE_EXTENSION configuration option to `backend/app/config.py`
  - Update file writer service in `backend/app/services.py` to use configurable extension
  - Update both dev and prod endpoints to pass extension parameter
  - Add integration test to verify .jsontest files are created when extension is configured
  - Path: `backend/app/config.py`, `backend/app/services.py`, `backend/app/routes.py`

- T022 [P] Implement NewWebSiteDomain prepopulation for Dev modal
  - Add JavaScript logic to `backend/static/main.js` to auto-populate domain field with pattern `qa-{DatabaseName}.showare.net`
  - Trigger prepopulation when DatabaseName field changes (onchange/oninput events)
  - Allow operators to edit the prepopulated value
  - Add validation to ensure prepopulated pattern matches expected format
  - Path: `backend/static/main.js`

## Dependencies
- Tests (T004-T007) before implementation (T008-T013)
- T008 config loader blocks many items dependent on constants
- T009 (FileWriter) blocks T011 and T012
- T010 (DB service) blocks T014
- T021 (configurable extension) requires T008 (config loader) and T009 (file writer)
- T022 (domain prepopulation) requires T013 (UI implementation)

## Parallel Example
```
# Launch T004-T007 together:
Task: "Contract test POST /api/jobs/dev in backend/tests/contract/test_post_dev_job.py" [P]
Task: "Contract test POST /api/jobs/prod in backend/tests/contract/test_post_prod_job.py" [P]
Task: "Integration test ready systems query in backend/tests/integration/test_ready_systems_query.py" [P]
Task: "Integration test file writer in backend/tests/integration/test_file_writer.py" [P]
```

## Notes
- Follow TDD: ensure contract tests fail before implementing
- Use timestamp+short-uuid filename pattern to avoid collisions
- Use atomic file writes (write to temp file then move/rename)
- Ensure app user has write access to `QUEUE_FOLDER`

## Task Generation Rules Applied
- Contract files generated contract tests (T004, T005)
- Entities in data-model mapped to model/service tasks (T009, T010)
- Endpoints mapped to implementation tasks (T011, T012)
