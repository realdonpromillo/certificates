from flask import render_template, request
from app import db
from app.errors import bp
from app.api.errors import error_response as api_error_response

# Übernommen aus den Beispielen von Miguel Grinberg
def wants_json_response():
    return request.accept_mimetypes['application/json'] >= \
        request.accept_mimetypes['text/html']

# Eigententicklung
@bp.app_errorhandler(400)
def invalid_data(error):
    if wants_json_response():
        return api_error_response(400)
    return render_template('errors/400.html'), 400

# Eigententicklung
@bp.app_errorhandler(403)
def forbidden(error):
    if wants_json_response():
        return api_error_response(403)
    return render_template('errors/403.html'), 403

# Übernommen aus den Beispielen von Miguel Grinberg
@bp.app_errorhandler(404)
def not_found_error(error):
    if wants_json_response():
        return api_error_response(404)
    return render_template('errors/404.html'), 404

# Übernommen aus den Beispielen von Miguel Grinberg
@bp.app_errorhandler(500)
def internal_error(error):
    db.session.rollback()
    if wants_json_response():
        return api_error_response(500)
    return render_template('errors/500.html'), 500

