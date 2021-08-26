# for database

from app import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from hashlib import md5

class Usernames(db.Model, UserMixin):

    # Set tablename 
    __tablename__ = 'usernames'

    # Table columns, including username, pass hash
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True, unique=True)
    pass_hash = db.Column(db.String)
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)

    # Image ratings will be stored here
    ratings = db.relationship('Ratings', backref='rater', lazy='dynamic')

    # Admin and Bot can broadcast messages
    broadcasts = db.relationship('Broadcasts', backref='mod', lazy='dynamic')

    # Scan ratings (will replace the ratings table later)
    scan_ratings = db.relationship('ScanRater', backref='scan_rater', lazy = 'dynamic')

    # Password hash function for security
    def set_password(self, password):
        self.pass_hash = generate_password_hash(password)

    # Check if correct password is put
    def check_password_hash(self, password):
        return check_password_hash(self.pass_hash, password)

    # Avatar generation for profiles (might fix later, maybe not important)
    def avatar(self, size):
        digest = md5(self.username.lower().encode('utf-8')).hexdigest()
        return 'https://gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def __repr__(self):
        return '<username: {}>'.format(self.username)

@login.user_loader
def load_user(id):
    return Usernames.query.get(int(id))

class Ratings(db.Model):

    __tablename__ = 'pic_ratings'

    id = db.Column(db.Integer, primary_key=True)
    img_name = db.Column(db.String, index=True)
    rating = db.Column(db.Integer, index=True)
    notes = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('usernames.id'))

    def __repr__(self):
        return '<Rating {}>'.format(self.rating)

class ScanRater(db.Model):

    __tablename__ = 'scan_ratings'

    id = db.Column(db.Integer, primary_key=True)
    subj_name = db.Column(db.String, index=True)
    scan_type = db.Column(db.String, index = True)
    scene = db.Column(db.String, index=True)
    distort_notes = db.Column(db.String, index=True)
    SBF_corr_notes = db.Column(db.String, index=True)
    full_brain_notes = db.Column(db.String, index=True)
    CIFTI_notes = db.Column(db.String, index=True)
    dropout_notes = db.Column(db.String, index=True)
    rating = db.Column(db.Integer, index=True)
    notes = db.Column(db.String)
    user_id = db.Column(db.Integer, db.ForeignKey('usernames.id'))

    def __repr__(self):
        return '<Rating of Scan {}>'.format(self.rating)

class Broadcasts(db.Model):

    __tablename__ = 'broadcasts'

    id = db.Column(db.Integer, primary_key=True)
    broadcast = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('usernames.id'))