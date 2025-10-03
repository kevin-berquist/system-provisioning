# Research: ShoWare System Setup

## Decisions

- Decision: Proceed without additional clarifications per stakeholder instruction.
  - Rationale: User explicitly allowed proceeding. Remaining assumptions documented below.

- Decision: Authentication & Authorization
  - Choice: Rely on network/host access controls and internal deployment to limit access to operations team (no app-level auth required by default).
  - Rationale: Keeps app simple and deployable in constrained ops environments; avoids adding external auth dependencies. If later required, add optional SSO integration.

- Decision: Filename Pattern
  - Choice: Use `DEV` and `PROD` job filenames with pattern: `<type>-YYYYMMDD-HHMMSS-<short-uuid>.json` (e.g., `dev-20251002-153012-3f7a9.json`).
  - Rationale: Guarantees uniqueness, readable timestamps, and no collisions.

- Decision: Constants Override Policy
  - Choice: Do NOT allow overriding constants (DatabaseServer, WebServer, Version) via UI. Constants configurable via server-side settings and require maintainer approval to change.
  - Rationale: Prevents accidental environment drift and maintains simple UI surface.

## Integration Research

- IIS hosting guidance:
  - Option A: Host Flask via WSGI (wfastcgi or IIS ARR) - recommended for pure Python stacks.
  - Option B: Run the Flask app as a Windows service and expose via reverse-proxy to IIS.
  - Recommendation: Provide documentation and a helper PowerShell script for IIS deployment (wfastcgi setup) and a sample web.config.

- MS SQL connectivity:
  - Use ODBC driver + pyodbc to connect to MS SQL Server. Keep DB access minimal and use parameterized queries.

## Research Tasks
- R-001: Document IIS hosting steps (wfastcgi + web.config + sample run_iis.ps1).
- R-002: Validate pyodbc connection patterns on Windows + CI testing instructions.
- R-003: Propose tests for contract testing of JSON output and DB query results.

## Output
- research.md completed with decisions above.
