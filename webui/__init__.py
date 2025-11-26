from flask import Flask


def create_app():
    # static_folder and template_folder are relative to this package
    app = Flask(__name__, static_folder='static', template_folder='templates')
    from . import routes
    app.register_blueprint(routes.bp)
    return app
