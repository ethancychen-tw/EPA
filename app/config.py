import os

config_path = os.path.abspath(os.path.dirname(__file__))

# Environment variables
if os.path.exists('config.env'):
    for line in open('config.env', 'r'):
        var = line.strip().split('=', 1)
        if len(var) == 2:
            os.environ[var[0]] = var[1].replace("\"", "")


class Config:
    # app
    APP_NAME = os.environ.get('APP_NAME')
    if os.environ.get('SECRET_KEY'):
        SECRET_KEY = os.environ.get('SECRET_KEY')
    else:
        SECRET_KEY = 'SECRET_KEY_ENV_VAR_NOT_SET'
        print('SECRET KEY ENV VAR NOT SET! SHOULD NOT SEE IN PRODUCTION')

    # db
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # email
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = os.environ.get('MAIL_PORT', 465)
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', True)
    if MAIL_USE_SSL == 'True':
        MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'username')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'password')

    # ISSUE REPORT GOOGLE FORM
    ISSUE_REPORT_GOOGLE_FORM_URL=os.environ.get('ISSUE_REPORT_GOOGLE_FORM_URL', 'username')
    ISSUE_REPORT_GOOGLE_FORM_NAME_FIELD_ID=os.environ.get('ISSUE_REPORT_GOOGLE_FORM_NAME_FIELD_ID', 'username')
    ISSUE_REPORT_GOOGLE_FORM_INTERNAL_GROUP_FIELD_ID=os.environ.get('ISSUE_REPORT_GOOGLE_FORM_INTERNAL_GROUP_FIELD_ID', 'username')
    ISSUE_REPORT_GOOGLE_FORM_ROLE_FIELD_ID=os.environ.get('ISSUE_REPORT_GOOGLE_FORM_ROLE_FIELD_ID', 'username')
    ISSUE_REPORT_GOOGLE_FORM_EMAIL_FIELD_ID=os.environ.get('ISSUE_REPORT_GOOGLE_FORM_EMAIL_FIELD_ID', 'username')

    # some other configs
    REVIEW_PER_PAGE = int(os.environ.get('REVIEW_PER_PAGE', 20))

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    STATIC_FOLDER = "static"
    DEBUG = True
    SQLALCHEMY_ECHO = False

    # linebot
    LINEBOT_MSG_CHANNEL_ACCESS_TOKEN = os.environ.get('DEV_LINEBOT_MSG_CHANNEL_ACCESS_TOKEN', None)
    LINEBOT_MSG_CHANNEL_SECRET = os.environ.get('DEV_LINEBOT_MSG_CHANNEL_SECRET', None)
    if not LINEBOT_MSG_CHANNEL_ACCESS_TOKEN or not LINEBOT_MSG_CHANNEL_SECRET:
        print("line bot not set!!! ")

    @staticmethod
    def init_app(app):
        Config.init_app(app)
        if not os.environ.get('SECRET_KEY'):
            raise Exception('DEVELOPMENT: SECRET_KEY IS NOT SET!')

class StagingConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL')
    
    STATIC_FOLDER = "static"
    DEBUG = False
    SQLALCHEMY_ECHO = False

    # linebot
    LINEBOT_MSG_CHANNEL_ACCESS_TOKEN = os.environ.get('STAGING_LINEBOT_MSG_CHANNEL_ACCESS_TOKEN', None)
    LINEBOT_MSG_CHANNEL_SECRET = os.environ.get('STAGING_LINEBOT_MSG_CHANNEL_SECRET', None)
    if not LINEBOT_MSG_CHANNEL_ACCESS_TOKEN or not LINEBOT_MSG_CHANNEL_SECRET:
        print("line bot not set!!! ")
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        if not os.environ.get('SECRET_KEY'):
            raise Exception('STAGING: SECRET_KEY IS NOT SET!')

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('PROD_DATABASE_URL')

    DEBUG = False
    SQLALCHEMY_ECHO = False

    # linebot
    LINEBOT_MSG_CHANNEL_ACCESS_TOKEN = os.environ.get('PRODUCTION_LINEBOT_MSG_CHANNEL_ACCESS_TOKEN', None)
    LINEBOT_MSG_CHANNEL_SECRET = os.environ.get('PRODUCTION_LINEBOT_MSG_CHANNEL_SECRET', None)
    if not LINEBOT_MSG_CHANNEL_ACCESS_TOKEN or not LINEBOT_MSG_CHANNEL_SECRET:
        print("line bot not set!!! ")
    @staticmethod
    def init_app(app):
        Config.init_app(app)
        if not os.environ.get('SECRET_KEY'):
            raise Exception('PRODUCTION: SECRET_KEY IS NOT SET!')


config = {
    'development': DevelopmentConfig,
    'staging': StagingConfig,
    'production': ProductionConfig
}