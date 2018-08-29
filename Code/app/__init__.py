from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import config
from werkzeug.contrib.fixers import ProxyFix
from flask_dance.contrib.google import make_google_blueprint
from raven.contrib.flask import Sentry


bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
login_manager.login_view = 'auth.login'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    app.wsgi_app = ProxyFix(app.wsgi_app)
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    login_manager.init_app(app)
    # with app.test_request_context():
    #     db.create_all()

    sentry = Sentry(app)
    google_bp = make_google_blueprint(scope=['https://www.googleapis.com/auth/userinfo.profile', 'https://www.googleapis.com/auth/userinfo.email'],
                                      offline=True, reprompt_consent=True,
                                      redirect_url= 'http://localhost:5000/auth/login_with_google')


    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    app.register_blueprint(google_bp, url_prefix="/auth")

    from .operation import operation as operation_blueprint
    app.register_blueprint(operation_blueprint)

    return app
