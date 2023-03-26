from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from config import Config
from config import SwaggerConfig

# Übernommen aus den Beispielen
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
db.init_app(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'auth.login'
login.login_message = ('Please log in to access this page.')

# Übernommen aus den Beispielen
bootstrap = Bootstrap(app)


from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from app.auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

from app.main import bp as main_bp
app.register_blueprint(main_bp)

from app.api import bp as api_bp
app.register_blueprint(api_bp, url_prefix='/api')

app.register_blueprint(SwaggerConfig.SWAGGERUI_BLUEPRINT, url_prefix=SwaggerConfig.SWAGGER_URL)

from app import models