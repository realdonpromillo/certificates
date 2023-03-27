from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import Config
from config import SwaggerConfig

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize SQLAlchemy
db = SQLAlchemy()
db.init_app(app)
migrate = Migrate(app, db)

## Initialize LoginManager
login = LoginManager(app)
login.login_view = 'auth.login'
login.login_message = ('Please log in to access this page.')

# Übernommen aus den Beispielen von Miguel Grinberg
bootstrap = Bootstrap(app)

# Übernommen aus den Beispielen von Miguel Grinberg
# Um ein Blueprint in Flask zu erstellen, wird eine neue Instanz der Blueprint-Klasse erstellt, 
# der dann Routen, Vorlagen und Funktionen hinzugefügt werden können. 
# Sobald ein Blueprint erstellt ist, kann er in der Hauptanwendung registriert werden und wird dann als Teil der Anwendung behandelt.

from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from app.auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

from app.main import bp as main_bp
app.register_blueprint(main_bp)

from app.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')

# Register Swagger Blueprint
app.register_blueprint(SwaggerConfig.SWAGGERUI_BLUEPRINT, url_prefix=SwaggerConfig.SWAGGER_URL)

from app import models