import urllib.error
import urllib.request

from flask import Flask, current_app, request

def create_app(config_object=None):
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    if config_object:
        app.config.from_object(config_object)
    else:
        # load from environment if present
        from .config import load_config
        load_config(app)

    @app.before_request
    def _enforce_authentication():
        if not current_app.config.get('ENFORCE_AUTH'):
            return None

        auth_url = current_app.config.get('AUTH_URL')
        if not auth_url:
            return ("Unauthorized", 401)

        user_account = request.cookies.get('UserAccount')
        if not user_account:
            return ("Unauthorized", 401)

        req = urllib.request.Request(auth_url)
        req.add_header('Cookie', f'UserAccount={user_account}')

        debug_auth = current_app.config.get('DEBUG_AUTH_REQUEST', False)
        debug_info = []

        if debug_auth:
            debug_info.append(f"Request URL: {auth_url}")
            debug_info.append(f"Request Headers: {dict(req.headers)}")

        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = resp.read().decode('utf-8', errors='ignore')
                if debug_auth:
                    debug_info.append(f"Response Content: {body}")
                    debug_info.append(f"Response Headers: {dict(resp.headers)}")
        except (urllib.error.URLError, ValueError) as exc:
            if debug_auth:
                debug_info.append(f"Request failed: {exc}")
                debug_info.append(f"Final Status: Authentication failed (request error)")
                debug_response = "\n".join(debug_info)
                return (debug_response, 200, {'Content-Type': 'text/plain'})
            current_app.logger.warning('Auth probe failed: %s', exc)
            return ("Unauthorized", 401)

        if 'AUTH OK' not in body:
            if debug_auth:
                debug_info.append(f"Final Status: Authentication denied - 'AUTH OK' not found in response")
                debug_response = "\n".join(debug_info)
                return (debug_response, 200, {'Content-Type': 'text/plain'})
            return ("Unauthorized", 401)

        if debug_auth:
            debug_info.append(f"Final Status: Authentication successful - 'AUTH OK' found in response")
            debug_response = "\n".join(debug_info)
            return (debug_response, 200, {'Content-Type': 'text/plain'})

    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
