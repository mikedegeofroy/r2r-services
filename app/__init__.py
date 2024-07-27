from flask import Flask
from flasgger import Swagger

def create_app():
    app = Flask(__name__)
    swagger = Swagger(app)

    with app.app_context():
        # Import routes
        from . import routes

    return app
