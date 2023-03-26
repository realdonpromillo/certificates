import os
from dotenv import load_dotenv
from flask_swagger_ui import get_swaggerui_blueprint

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'SECURITY_KEY_FORMS'
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        CERTIFICATES_PER_PAGE = 10

class SwaggerConfig(object):
        SWAGGER_URL = '/swagger'
        API_URL = '/static/swagger.json'
        SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
                SWAGGER_URL,
                API_URL,
                config={
                        'app_name': "Certificates and Users API"
                }
        )