from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import DefaultConfig
from flask_login import LoginManager
import os
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(DefaultConfig)
#app.config['UPLOAD_PATH'] = '/static/uploads'
db = SQLAlchemy(app)
migrate = Migrate (app, db)

login = LoginManager(app)
login.login_view = 'login'

bootstrap = Bootstrap(app)

# Ensures email logger runs during production
# DOES NOT WORK AS INTENDED, FIX LATER (bug) --fixed--
if not app.debug:
   if app.config['MAIL_SERVER']:
      auth = None
      if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
         auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
      secure = None
      if app.config['MAIL_USE_TLS']:
         secure = ()
      mail_handler = SMTPHandler(mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                                 fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                                 toaddrs=app.config['ADMINS'], subject='Braincheck [BETA] Failure',
                                 credentials=auth, secure=secure)
      mail_handler.setLevel(logging.ERROR)
      app.logger.addHandler(mail_handler)

   if app.config['LOG_TO_STDOUT']:
      stream_handler = logging.StreamHandler()
      stream_handler.setLevel(logging.INFO)
      app.logger.addHandler(stream_handler)
   else:
      # Creates logs
      if not os.path.exists('logs'):
         os.mkdir('logs')
      file_handler = RotatingFileHandler('logs/braincheck.log', maxBytes=10287, backupCount=10)
      file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d'))
      file_handler.setLevel(logging.INFO)
      app.logger.addHandler(file_handler)
      app.logger.info('Braincheck Startup Info')

from app import routes, models, errors