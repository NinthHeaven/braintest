# CUSTOM MADE ERROR MESSAGES
# These are more of a "Oh no a bug has been found!" type message instead of the "SERVER 404" type message

from flask import render_template
from app import app, db

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404
    
@app.errorhandler(500)
def interval_error(error):
    db.session.rollback()
    return render_template('500.html'), 500