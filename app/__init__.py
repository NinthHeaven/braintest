from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import DefaultConfig
from flask_login import LoginManager
import os
import logging
from logging.handlers import RotatingFileHandler, SMTPHandler
from flask_bootstrap import Bootstrap

# TESTING FOR HTTPS: https://stackoverflow.com/questions/29458548/can-you-add-https-functionality-to-a-python-flask-web-server
# TODO: FIX
#import ssl

#context = ssl.SSLContext()
#context.load_cert_chain('server.crt', 'server.key')


# Initiate the app
app = Flask(__name__)
app.config.from_object(DefaultConfig)
# if name == "__main__":
   #app.run(ssl_context=context)

# I feel like I'll need to use for break loops later...
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
db = SQLAlchemy(app)
migrate = Migrate (app, db)

# Check to see who is logged on
login = LoginManager(app)
login.login_view = 'login'

# Apply bootstrap because web design is hard
bootstrap = Bootstrap(app)

# Ensures email logger runs during production
# DOES NOT WORK AS INTENDED, FIX LATER (bug) --fixed-- --not fixed again :(--
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
                                 toaddrs=app.config['ADMINS'], subject='Braincheck [ALPHA] Failure',
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