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

        try:
            with urllib.request.urlopen(req, timeout=5) as resp:
                body = resp.read().decode('utf-8', errors='ignore')
        except (urllib.error.URLError, ValueError) as exc:
            current_app.logger.warning('Auth probe failed: %s', exc)
            return ("Unauthorized", 401)

        if 'AUTH OK' not in body:
            return ("Unauthorized", 401)

    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
