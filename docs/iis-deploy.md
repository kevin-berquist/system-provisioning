# IIS Deployment Notes for ShoWare System Setup

Recommended approach: use wfastcgi to host Flask under IIS (Windows).

Basic steps:
1. Install Microsoft IIS and CGI features.
2. Install Python and the wfastcgi package.
3. Create a web.config that points to the Flask WSGI entry (backend.run:app) and configure environment variables.
4. Use the included `backend/run_iis.ps1` to assist with registering the WSGI handler and configuring the site.

Provide example web.config and run_iis.ps1 in the backend/ directory.
