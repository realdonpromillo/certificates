from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth
from app.models import User
from app.api.errors import error_response
from flask import g

basic_auth = HTTPBasicAuth()
token_auth = HTTPTokenAuth()

# Übernommen aus den Beispielen von Miguel Grinberg
# Eigenentwicklung: g.user = user
@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        # Globaler Zugriff auf den User
        g.user = user
    return user

# Übernommen aus den Beispielen von Miguel Grinberg
@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)

# Übernommen aus den Beispielen von Miguel Grinberg
# Eigenentwicklung: g.user = user
@token_auth.verify_token
def verify_token(token):
    user = User.check_token(token) if token else None
    if user:
        # Globaler Zugriff auf den User
        g.user = user
    return user

# Übernommen aus den Beispielen von Miguel Grinberg
@token_auth.error_handler
def token_auth_error(status):
    return error_response(status)