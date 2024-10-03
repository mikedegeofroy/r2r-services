from flask import Blueprint

from dotenv import load_dotenv
load_dotenv(override=True)

generate = Blueprint('generator', __name__, template_folder='templates')

from app.generate import routes