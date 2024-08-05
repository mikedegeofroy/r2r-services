from flask import Blueprint

generate = Blueprint('generator', __name__, template_folder='templates')

from app.generate import routes