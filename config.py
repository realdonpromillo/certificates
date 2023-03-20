import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config(object):
        SECRET_KEY = os.environ.get('SECRET_KEY') or 'SECURITY_KEY_FORMS'
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
        CERTIFICATES_PER_PAGE = 10
        LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')