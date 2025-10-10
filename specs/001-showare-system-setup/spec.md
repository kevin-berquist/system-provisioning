# Feature Specification: ShoWare System Setup

**Feature Branch**: `001-showare-system-setup`  
**Created**: 2025-10-02  
**Status**: Draft  
**Input**: User description: "Develop a web application named ShoWare System Setup that lets operations team members create JSON job files in a monitored Queue folder to request automated Dev and Prod site setups. The app lists queued and running jobs (based on files in the queue and running folders) and lists ShoWare systems ready for production (based on a provided database query). The app provides actions to Create Dev Site and to Setup Production per ready system. Dev JSON example and Prod JSON example provided; certain fields are constants and are not filled by users; some values (for production) are pre-filled from a control DB query."

## Execution Flow (main)
```
1. Parse user description from Input
   → If empty: ERROR "No feature description provided"
2. Extract key concepts from description
   → Identify: actors, actions, data, constraints
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
   → If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
   → Each requirement must be testable
   → Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
   → If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   → If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation
When creating this spec from a user prompt:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption you'd need to make
2. **Don't guess**: If the prompt doesn't specify something (e.g., "login system" without auth method), mark it
3. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
4. **Common underspecified areas**:
   - User types and permissions
   - Data retention/deletion policies  
   - Performance targets and scale
   - Error handling behaviors
   - Integration requirements
   - Security/compliance needs

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
As an Operations team member, I want a simple web interface where I can:
- Create a Dev site by filling a small form which drops a correctly formatted JSON file into a repository's `queue` folder (the pre-existing provisioning service will consume that file).
- See what jobs are currently queued (files present in the `queue` folder) and what jobs are running (files present in the `running` folder).
- See a list of ShoWare systems that are ready for production (populated from the ShoWare control DB by a provided query) and click a button to create a Prod setup job JSON for a chosen ready system.

Rationale: operations personnel need a low-friction way to create the JSON files that an existing provisioning pipeline consumes. The app does not perform provisioning itself — it only writes job files and provides visibility into queue/running state and production-ready systems.

### Acceptance Scenarios
1. **Given** the `queue` folder is accessible and the user clicks "Create Dev Site" and submits required fields, **When** the form is valid, **Then** the app writes a JSON file into the `queue` folder with JobType `DEV_SETUP` and all required fields; the pre-existing provisioning service will later move the file to `running` and `completed` as it processes it.
2. **Given** the `queue` and `running` folders are accessible, **When** the main screen is loaded, **Then** the app lists the files currently in `queue` and `running` (file name and timestamp) and indicates their counts. Each entry in the Queued Jobs and Running Jobs lists MUST show at minimum:

   - Name (if the JSON payload contains ShoWareControl, NewShoWareControlName or the file metadata provides a human-friendly name)
   - DatabaseName
   - CurrentDevWebSiteDomain (if present in the payload) — presented as the dev site URL

   If a job file's JSON is malformed or missing fields, the UI MUST still present the file (using filename and timestamp) and display a clear placeholder such as "(missing metadata)" for missing values.
3. **Given** the ShoWare control database is reachable and the control query returns rows, **When** the main screen is loaded, **Then** the app shows a list of systems that match the supplied query and displays a "Setup Production" button for each listed system. Each row in the Ready for Production list MUST include, at minimum:

   - Name
   - DatabaseName
   - CurrentDevWebSiteDomain (dev site URL)

   The UI should present these fields prominently so operators can quickly identify the correct system to act on.

   **Additionally**, the Ready for Production list MUST exclude any system that already has a production job (queued or running) with the same DatabaseName to prevent duplicate production setups. The app MUST scan both the `queue` and `running` folders for `PROD_SETUP` job files, extract the DatabaseName from each JSON payload, and filter out any Ready system with a matching DatabaseName.
4. **Given** a user clicks "Setup Production" for a ready system, **When** the setup modal opens, **Then** the modal MUST prominently display the selected system's Name and CurrentDevWebSiteDomain (dev site URL) so the operator can confirm the target system.

   The Setup Production modal MUST collect the following inputs from the user before creating the job JSON:

   - WebServerCluster (select) — required, options come from `PROD_WEBSERVER_CLUSTER_OPTIONS` (e.g., us-c1webx, us-c2webx, au-c1webx, uk-c1webx)
   - NewDatabaseServer (select) — required, options come from `PROD_DATABASE_SERVER_OPTIONS` (e.g., us-clusdb1, us-clusdb2, au-clusdb1, uk-clusdb1)
   - NewWebSiteDomain (text field) — required, must be provided by the operator in a valid domain format (e.g., "prod.example.showare.net"). The app MUST validate the domain format before allowing submission.

   When the operator confirms, **Then** the app writes a JSON file into the `queue` folder with JobType `PROD_SETUP` and required production fields (constants filled by the app, values selected by the user for WebServerCluster/NewDatabaseServer/NewWebSiteDomain). The selected system's DatabaseName/CurrentDevWebSiteDomain/GeminiProjID MUST be included in the payload.

   Additionally, the produced `PROD_SETUP` JSON MUST include a `ShoWareControl` field containing the canonical ShoWare control `Name` value derived from the Ready row used to open the modal. The UI MUST prefer `ShoWareControl` when displaying the name for Prod-originated job entries in Queued and Running lists. If `ShoWareControl` is absent, the UI should fall back to `NewShoWareControlName` or a filename-derived placeholder.

   NOTE: The Setup Production modal MUST NOT collect NewShoWareControlName or DatabaseName as input fields — those values are provided by the selected Ready row and must be displayed as read-only confirmation fields in the modal. Operators should not be able to edit DatabaseName or the system's canonical Name from the Production modal.

5. **Given** there are existing `PROD_SETUP` job files in the `queue` or `running` folders with DatabaseName "MyTestDB", **When** the main screen loads the Ready for Production list, **Then** any system with DatabaseName "MyTestDB" MUST be excluded from the Ready list to prevent duplicate production setups. The filtering MUST work regardless of whether the existing job is queued (pending) or running (in progress).

### Edge Cases
- The `queue` or `running` directory is not present or permissions prevent writing/reading → the app should show a clear error and guidance to operators.
- Two users simultaneously create a job with the same generated filename → ensure file naming avoids collisions (timestamp + UUID pattern).
- The control DB query is slow or unreachable → the app should show an offline/error state and allow retries.
- The provisioning service rejects or fails a job after it's moved to `running` → the app should not attempt to process files but could surface failure metadata if an external status API is available (NEEDS_CLARIFICATION).

### Edge Cases
- What happens when [boundary condition]?
- How does system handle [error scenario]?

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: The app MUST present a Create Dev Site form. The form fields that the user must provide are:
   - NewShoWareControlName (string)
   - DatabaseName (string)
   - NewWebSiteDomain (string) — the UI MUST prepopulate this field with the pattern `qa-{DatabaseName}.showare.net` where `{DatabaseName}` is the value entered in the DatabaseName field. The prepopulated value can be edited by the operator if needed.
   - GeminiTaskID (string) — optional, may default to `000000` if not provided
   The app MUST populate the remaining Dev JSON fields automatically (JobType = `DEV_SETUP`, DatabaseServer, WebServer, NewSystemVersion are constants configured in app settings).

- **FR-002**: The app MUST write a well-formed JSON file into the configured `queue` folder when the Dev form is submitted. The filename MUST be unique and include a timestamp and short identifier (e.g., `devsetup-YYYYMMDD-HHMMSS-<rand>.json`).

- **FR-003**: The app MUST list files present in the configured `queue` folder (show file name, creation time) and list files present in the configured `running` folder.

- **FR-004**: The app MUST query the ShoWare control database using the supplied SQL to determine systems ready for production and display the returned rows with at least Name, DatabaseName, GeminiProjID, CurrentDevWebSiteDomain. The list MUST exclude systems that already have production jobs (queued or running) with the same DatabaseName to prevent duplicate production setups.

- **FR-005**: The app MUST provide a "Setup Production" action for each ready system. When selected, the app MUST open a modal that:

   - Displays the selected system's Name and CurrentDevWebSiteDomain clearly
   - Presents input fields for WebServerCluster and NewDatabaseServer (required selects with options supplied by `PROD_WEBSERVER_CLUSTER_OPTIONS` and `PROD_DATABASE_SERVER_OPTIONS` respectively) and NewWebSiteDomain (required text field that must be provided by the operator in valid domain format).

   After the operator confirms valid inputs, the app MUST write a PROD_SETUP JSON into the `queue` folder with JobType `PROD_SETUP`, Version (constant), the selected/entered values, and the selected system's identifying fields.

- **FR-006**: The app MUST NOT move, delete, or otherwise process job files beyond writing the JSON file to the `queue` folder and reading `queue`/`running` directory contents.

- **FR-007**: The app MUST validate user inputs and present user-facing errors:
   - Domain format validation for NewWebSiteDomain (both Dev and Production jobs)
   - Non-empty validation for DatabaseName/NewShoWareControlName (Dev jobs)
   - Required field validation for Production jobs including NewWebSiteDomain
   - All validation errors MUST be displayed as inline messages within the modal interface

- **FR-007-ui**: The app's main screen and input flows MUST present a modern, sleek user interface. Inputs that require additional information (Create Dev Site, Setup Production) MUST use in-page modal dialogs or slide-over panels with form fields and inline validation. The implementation MUST NOT use native JavaScript prompt() dialogs or alert() for collecting input; these are disallowed.

   The validation behavior called out in FR-007 should surface inline validation messages inside the modal and prevent submission until required fields are satisfied.

- **FR-008**: The app MUST log operations (create job, write file, DB query status, errors) with sufficient detail for operators to diagnose issues.

- **FR-009**: The app MUST support configuration of constants and folder paths via a simple server-side configuration (e.g., appsettings or environment variables): `QUEUE_FOLDER`, `RUNNING_FOLDER`, `COMPLETED_FOLDER`, `DEV_DATABASE_SERVER`, `DEV_WEBSERVER`, `DEV_SYSTEM_VERSION`, `PROD_VERSION`, `PROD_WEBSERVER_CLUSTER_OPTIONS`, `PROD_DATABASE_SERVER_OPTIONS`, `CONTROL_DB_CONNECTION`.

 - **FR-013**: Development-only output extension option: The app MUST expose a server-side configuration option that, when enabled for a development or test deployment, causes newly created job files to be written with the extension `.jsontest` instead of `.json.``
    - Purpose: Prevent the pre-existing provisioning pipeline (which only monitors `.json` files) from automatically consuming test artifacts that are intended for manual inspection on remote/target machines.
    - Behavior:
       - When the option is disabled (default), the app writes job files with the normal `.json` extension and behavior is unchanged.
       - When the option is enabled, the app writes job files with the same filename base but uses the `.jsontest` extension (for example: `devsetup-20251009-120000-abc123.jsontest` or `prodsetup-20251009-120000-xyz789.jsontest`).
       - The change is purely an output filename extension substitution; the JSON payload structure, metadata fields (including `ShoWareControl`), and written timestamps MUST remain unchanged.
    - Acceptable configuration surface (examples): a boolean flag or a configurable `JOB_FILE_EXTENSION` value scoped to non-production deployments. The spec intentionally leaves the exact configuration mechanism open (environment variable, config file, or toggle) but requires that it be documented and default to writing `.json` in production.
    - Testable acceptance criteria:
       - Given the dev/test extension option is enabled, when a user creates a Dev or Prod job, then the resulting file in the configured `QUEUE_FOLDER` MUST use the `.jsontest` extension and be discoverable via file listing.
       - Given the option is enabled, the pre-existing provisioning pipeline which filters for `.json` files MUST not pick up `.jsontest` files (this is an external-system behavior to be validated by operators; the app must simply produce `.jsontest` files when enabled).
       - Given the option is enabled, the UI and listing pages MUST still show the generated filename and remain able to display payload-derived metadata when the app reads the file content for listing purposes.

*Open questions / NEEDS_CLARIFICATION*:
- **FR-010**: Authentication / authorization: who can create jobs? The prompt doesn't specify; do we require login or restrict via network/host? [NEEDS_CLARIFICATION]
- **FR-011**: File ownership / naming conventions: any organization-specific filename pattern required? (We propose timestamp+uuid) [NEEDS_CLARIFICATION]
- **FR-012**: Should the app allow overriding constant fields in exceptional cases (e.g., non-standard WebServer or DatabaseServer)? [NEEDS_CLARIFICATION]

*Example of marking unclear requirements:*
- **FR-006**: System MUST authenticate users via [NEEDS CLARIFICATION: auth method not specified - email/password, SSO, OAuth?]
- **FR-007**: System MUST retain user data for [NEEDS CLARIFICATION: retention period not specified]

### Key Entities *(include if feature involves data)*
- **DevJobRequest**: represents a dev site creation request. Attributes: NewShoWareControlName, DatabaseName, DatabaseServer (constant), WebServer (constant), NewWebSiteDomain, NewSystemVersion (constant), GeminiTaskID, CreatedAt, Filename.
- **ProdJobRequest**: represents a prod site creation request. Attributes: WebServerCluster, NewDatabaseServer, DatabaseName, CurrentDevWebSiteDomain, NewWebSiteDomain, Version (constant), GeminiProjID, CreatedAt, Filename.
- **ReadySystemRow**: a row from the ShoWare control DB query. Attributes: Name, DatabaseName, GeminiProjID, CurrentDevWebSiteDomain.

## Review & Acceptance Checklist (populated)

### Content Quality
- [x] No implementation details that assume a particular framework (we keep requirements generic)
- [x] Focused on user value and business needs
- [ ] Written for non-technical stakeholders (some implementation notes remain for the implementer)
- [x] All mandatory sections completed

### Requirement Completeness
- [ ] No [NEEDS_CLARIFICATION] markers remain (there are 3 listed: auth, filename policy, overriding constants)
- [x] Requirements are testable and unambiguous where specified
- [x] Success criteria are measurable (file created, correct JSON, lists populated)
- [x] Scope is clearly bounded: app writes files only and reads directories and control DB
- [x] Dependencies and assumptions identified (pre-existing provisioning service processes files; control DB schema/query provided)

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [ ] All mandatory sections completed

### Requirement Completeness
- [ ] No [NEEDS CLARIFICATION] markers remain
- [ ] Requirements are testable and unambiguous  
- [ ] Success criteria are measurable
- [ ] Scope is clearly bounded
- [ ] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked (see NEEDS_CLARIFICATION items)
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [ ] Review checklist passed (pending answers to NEEDS_CLARIFICATION)
---
