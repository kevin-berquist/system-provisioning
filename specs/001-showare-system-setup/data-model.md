# Data Model: ShoWare System Setup

## Entities

- DevJobRequest
  - NewShoWareControlName: string (required)
  - DatabaseName: string (required)
  - DatabaseServer: string (constant, e.g., `us-devdb`)
  - WebServer: string (constant, e.g., `us-devweb`)
  - NewWebSiteDomain: string (required, must validate domain format)
  - NewSystemVersion: string (constant)
  - GeminiTaskID: string (optional)
  - CreatedAt: datetime
  - Filename: string (unique file name written to queue)

- ProdJobRequest
  - WebServerCluster: enum (us-c1webx, us-c2webx, au-c1webx, uk-c1webx)
  - NewDatabaseServer: enum (us-clusdb1, us-clusdb2, au-clusdb1, uk-clusdb1)
  - DatabaseName: string (sourced from ReadySystemRow; MUST NOT be collected from the operator in the Production modal — presented as a read-only confirmation field)
  - CurrentDevWebSiteDomain: string (sourced from ReadySystemRow; presented read-only in the Production modal)
  - NewWebSiteDomain: string (derived for Prod flows; MUST be deterministically derived from `CurrentDevWebSiteDomain` and MUST NOT be editable or displayed to the operator in the Production modal)
  - Version: string (constant)
  - GeminiProjID: string (sourced from ReadySystemRow)
  - CreatedAt: datetime
  - Filename: string

- ReadySystemRow
  - Name: string
  - DatabaseName: string
  - GeminiProjID: integer
  - CurrentDevWebSiteDomain: string

### ShoWareControl

- ShoWareControl: string
  - Description: Canonical control name for a system; derived from `ReadySystemRow.Name` (control DB `Name` column).
  - Usage: Included in `PROD_SETUP` JSON payloads as the authoritative display name for Prod-originated job files and used by the UI when displaying queued/running jobs.

## Validation Rules
- NewWebSiteDomain must be a valid domain-like string and not empty.
- DatabaseName must match DB naming conventions (alphanumeric, dashes).
- GeminiProjID must be numeric and non-zero for production-ready rows.

Notes:
- For the Production modal, `Name` and `DatabaseName` are read-only confirmation fields supplied from the `ReadySystemRow`. Operators must not be able to edit these values in the Production modal.
- Validation of `DatabaseName` and `Name` is performed by ensuring the selected `ReadySystemRow` came from a successful control DB query; the modal should surface a clear error if the selected row is missing required fields.

## Relationships
- ReadySystemRow is not stored locally; it's read-only from control DB. ProdJobRequest is created using data from ReadySystemRow.
