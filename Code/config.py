import os

basedir = os.path.abspath(os.path.dirname(__file__))
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

class Config:

    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '465'))
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'true').lower() in \
                   ['true', 'on', '1']
    MAIL_USERNAME = "schoolselectionie@gmail.com"
    MAIL_PASSWORD = 'ABC12345!'
    FLASKY_MAIL_SUBJECT_PREFIX = '[BestChoice]'
    FLASKY_MAIL_SENDER = 'BestChoice Team <schoolselectionie@gmail.com>'
    POSTS_PER_PAGE = 10
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    GOOGLE_OAUTH_CLIENT_ID = "429221528820-0876ccgupb8rjtpl0730h2koa6vrklq7.apps.googleusercontent.com"
    GOOGLE_OAUTH_CLIENT_SECRET = "ds0ccAARoys3B-ppuOZO8j5N"
    UPLOAD_FOLDER = os.getcwd() + '/app/static/avatars/'
    FLASKY_ADMIN = 'school_selection@gmail.com'
    OAUTHLIB_RELAX_TOKEN_SCOPE = True
    OAUTHLIB_INSECURE_TRANSPORT = True

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:12345678@schools.cjakbty4kyuc.eu-west-1.rds.amazonaws.com/bestchoice'

config = {
    'development': DevelopmentConfig,
    'default': DevelopmentConfig
}
