from flask import Blueprint

transcribe = Blueprint('transcribe', __name__, template_folder='templates')

from app.transcribe import routes