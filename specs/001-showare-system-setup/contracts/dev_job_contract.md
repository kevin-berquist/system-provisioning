# Dev Job Contract

Endpoint: POST /api/jobs/dev

Request JSON (example):
{
  "JobType": "DEV_SETUP",
  "NewShoWareControlName": "Red House Entertainment, LLC - Paramount Center For The Arts-VIP",
  "DatabaseName": "dbname",
  "DatabaseServer": "us-devdb",
  "WebServer": "us-devweb",
  "NewWebSiteDomain": "qa-paramounthvvip.showare.net",
  "NewSystemVersion": "2.02.28",
  "GeminiTaskID": "000000"
}

Responses:
- 201 Created: { "filename": "dev-20251002-...json", "path": "C:/.../queue/dev-...json" }
- 400 Bad Request: validation errors
