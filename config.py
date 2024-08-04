from distutils.util import strtobool
from os import getenv

from dotenv import load_dotenv
load_dotenv() # Load environment variables from .env file

import logging
LOGGING_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
LOGGING_LEVEL = logging.INFO  # Adjust the log level as needed

#// APP-CONFIG
class Config:

    FLASK_APP = 'app.py'
    SECRET_KEY = getenv('SECRET_KEY')
    UPLOAD_FOLDER = getenv('upload_url')
    MAX_CONTENT_PATH = None
    LANGUAGES = ['en', 'es']
    MS_TRANSLATOR_KEY = getenv('MS_TRANSLATOR_KEY')
    ELASTICSEARCH_URL = getenv('ELASTICSEARCH_URL', None)
    # ELASTICSEARCH_URL=es_url
    POSTS_PER_PAGE = 25
    APP_LOGO = '/static/img/favicon/favicon32x32.png'
    ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'svg', 'jpg', 'jpeg', 'gif','mp4']

    LOG_TO_STDOUT = getenv('LOG_TO_STDOUT')
    LOGGING_FORMAT = LOGGING_FORMAT
    LOGGING_LEVEL = LOGGING_LEVEL
    SQLALCHEMY_ECHO = False

    #SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://root:@localhost:3306/empty" #mysql(no-password set, it's supposed to come after //root:)
    OAUTHLIB_INSECURE_TRANSPORT = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_ENGINE = {
    'rollback_on_exception': True,
    'autoflush': True,
    'expire_on_commit': False,
    }

    #prevents Shared Session Cookies
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True  # If using HTTPS
    #//
    SESSION_TYPE = 'redis' #//other-options('filesystem','mongodb') etc but'filesystem' is only suitable for small projects)
    #CACHE_TYPE = 'redis' #//other-options('simple', 'memcached', or 'filesystem')
    #CACHE_TYPE = 'simple' #//other-options('simple', 'memcached', or 'filesystem')

    REDIS_CONFIG = {
    'CACHE_TYPE': 'redis',
    'CACHE_KEY_PREFIX': 'server_1',
    'CACHE_REDIS_HOST': 'redis://localhost',
    'CACHE_REDIS_PORT': 6379,
    'CACHE_REDIS_URL': getenv('redis_url', 'redis://'),
    }

    #//MAIL
    RESET_PASS_TOKEN_MAX_AGE = 3600  # Example value in seconds(30min)
    MAIL_MAX_EMAILS = None
    MAIL_SUPPRESS_SEND = False
    MAIL_ASCII_ATTACHMENTS = True
    ADMINS = ['sales@net.co', 'chrisjsmez@gmail.com']
    #//
    
    MAIL_PORT = int(getenv('MAIL_PORT', 587))  # Ensure this is an integer
    MAIL_USE_TLS = bool(strtobool(getenv('MAIL_USE_TLS', 'False'))) #ensure type is compatible to avoid Flask-Mail [SSL: WRONG_VERSION_NUMBER] wrong version number (_ssl.c:1123)
    MAIL_USE_SSL = bool(strtobool(getenv('MAIL_USE_SSL', 'False')))
    # MAIL_USE_TLS = bool(getenv('MAIL_USE_TLS', True))
    # MAIL_USE_SSL = bool(getenv('MAIL_USE_SSL', False))
    # DEFAULT_MAIL_SENDER = getenv('DEFAULT_MAIL_SENDER')
    DEFAULT_MAIL_SENDER = ('Intellect', getenv('DEFAULT_MAIL_SENDER') ) 
    MAIL_SERVER = getenv('MAIL_SERVER')
    MAIL_USERNAME = getenv('MAIL_USERNAME')
    MAIL_PASSWORD = getenv('MAIL_PASSWORD')
    
    """ Mailtrap API """
    MAILTRAP_API_KEY = getenv('MAILTRAP_API_KEY')
    MAILTRAP_API_TOKEN = getenv('MAILTRAP_API_TOKEN')
    MAILTRAP_INBOX_ID = getenv('MAILTRAP_INBOX_ID')

class DevelopmentConfig(Config):
    FLASK_ENV = 'development'
    FLASK_DEBUG = True
    FLASK_APP = 'app.py'
    
    # Mail configurations
    # MAIL_DEBUG = True
    # DEFAULT_MAIL_TOKEN = getenv('mailtrap_token') 
    # MAIL_SERVER = getenv('mailtrap_server')
    # MAIL_PORT = getenv('mailtrap_port')
    # MAIL_USERNAME = getenv('mailtrap_username')
    # MAIL_PASSWORD = getenv('mailtrap_password')
    
    SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///')
    RAVE_SECRET_KEY = getenv('RAVE_TEST_SECRET_KEY')
    #SQLALCHEMY_ECHO = True
    #//SESSION_TYPE = 'filesystem'

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    FLASK_APP = 'passenger_wsgi.py'
    FLASK_ENV = 'production'

    SQLALCHEMY_DATABASE_URI = getenv('SQLALCHEMY_DATABASE_URI_PROD', 'sqlite:///')
    RAVE_SECRET_KEY = getenv('RAVE_LIVE_SECRET_KEY')

    # Add production-specific settings here
    
    #prevents Shared Session Cookies #// so that other similar browsers would not have access to same first logged-in user account
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True  # If using HTTPS
    #//SESSION_TYPE = 'redis' # 'filesystem', 'mongodb' etc #//only suitable for small projects

app_config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}
