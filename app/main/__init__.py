# Übernommen aus den Beispielen von Miguel Grinberg
from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes