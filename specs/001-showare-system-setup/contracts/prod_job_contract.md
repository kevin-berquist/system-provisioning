# Prod Job Contract

Endpoint: POST /api/jobs/prod

Request JSON (example):
{
  "JobType": "PROD_SETUP",
  "WebServerCluster": "us-c1webx",
  "NewDatabaseServer": "us-clusdb1",
  "DatabaseName": "ripleyschristmasspectacular",
  "CurrentDevWebSiteDomain": "qa-ripleyschristmasspectacular.showare.net",
  "NewWebSiteDomain": "ripleyschristmasspectacular.showare.com",
  "Version": "2.02.28",
  "GeminiProjID": "1979"
}

Responses:
- 201 Created: { "filename": "prod-20251002-...json", "path": "C:/.../queue/prod-...json" }
- 400 Bad Request: validation errors
