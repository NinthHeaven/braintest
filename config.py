# Configurations
import os
basedir = os.path.abspath(os.path.dirname(__file__))

# default config (for production)
class DefaultConfig(object):
    DEBUG = False
    SECRET_KEY = '~\xa5\xd36;\x8e\x98&\xcc\x00\x93E&\xcen\x91\xe1\xf6v\x19\x87\xd0\xd2\xab'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '').replace('postgres://', 'postgresql://') or 'sqlite:///' + os.path.join(basedir, 'usernames.db')
    SQLALCHEMY_TRACK_MODIFACTIONS = False
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['brainboterrors@gmail.com']
    MAX_CONTENT_LENGTH = 1024 * 1024

class devConfig(DefaultConfig):
    DEBUG = True