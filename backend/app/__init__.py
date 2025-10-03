from flask import Flask

def create_app(config_object=None):
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    if config_object:
        app.config.from_object(config_object)
    else:
        # load from environment if present
        from .config import load_config
        load_config(app)

    from .routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app
