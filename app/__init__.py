from flask import Flask
from flasgger import Swagger
from app.transcribe import transcribe
from app.generate import generate
from flask_cors import CORS

from dotenv import load_dotenv
load_dotenv(override=True)

def create_app():
    app = Flask(__name__)
    
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(transcribe, url_prefix='/transcribe')
    app.register_blueprint(generate, url_prefix='/avatar')

    swagger = Swagger(app)

    return app
