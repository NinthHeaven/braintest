from flask import render_template, redirect, url_for, request, flash, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.sql.elements import Null
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from app import app, db
from app.forms import ImgRating, Login, Register, EditProfile, Notifications, ImgUploader
from app.models import Usernames, Ratings, Broadcasts, ScanRater
from datetime import datetime
import os
import re
# Constantly update the time a user accesses the page
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# TODO: MODIFY LATER
@app.route("/")
@login_required
def home_page():
    # Create a temporary database connection
    users = db.session.query(Usernames).all()
    return render_template('home.html', users=users)

@app.route("/login", methods=['GET', 'POST'])
def login():
    # If the user is already logged in, get them back to the home page.
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = Login()
    # Check if username exists or if password matches
    if form.validate_on_submit():
        user = Usernames.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password_hash(form.password.data):
            flash("Invalid username or password.")
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)

        # Redirect user to page they wanted to access (might delete later)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('home_page')
        return redirect(next_page)
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home_page'))
    form = Register()
    if form.validate_on_submit():
        user = Usernames(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now registered!')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# TODO: display previous ratings
@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):
    user = Usernames.query.filter_by(username=username).first_or_404()
    announcements = db.session.query(Broadcasts).all()
    ## for admin and bot access only...
    form = Notifications()
    if form.validate_on_submit():
        message = Broadcasts(broadcast=form.notif.data)
        db.session.add(message)
        db.session.commit()
        flash('Message has been sent to the site.')
        return redirect(url_for('user', username=current_user.username))   
    return render_template('user.html', user=user, announcements=announcements, form=form)

# TODO: delete later...
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfile(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('user', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)

# TODO: for my eyes only
@app.route('/logs')
@login_required
def logs():
    return render_template('logs.html')





# THIS WILL BE NEW RATER FUNC, DELETE ANY DUPLICATES
@app.route('/rater', methods=['GET', 'POST'])
@login_required
def rater():
    files = os.listdir('app/static/subjects/HCD_wb1.4.2.pngs-selected/')
    subj_list = set()
    scantype_list = []
    # Get a list of the subjects and also the scan types (will be used for accessing other scans)
    for i in files:
        if i not in subj_list:
            subj_list.add(i.split('_V1_MR', 1)[0])
        scantype_list.append(i.split('_V1_MR_', 1)[1])

    # For rating stats for each subject
    total_files = len(files)
    subject_files = {}
    for s in subj_list:
        count = 0
        for file in files:
            if s in file:
                count+=1
                subject_files[s] = count
    total_ratings = db.session.query(ScanRater.subj_name, db.func.count()).group_by(ScanRater.subj_name).all()


    return render_template('rater.html', subj_list=subj_list, total_ratings=total_ratings, total_files=total_files, subject_files=subject_files)

@app.route('/subject/<subject>', methods=['GET', 'POST'])
@login_required
def subject_scans(subject):
    # Redundant line of code (probably will fix later)
    files = os.listdir('app/static/subjects/HCD_wb1.4.2.pngs-selected/')
    subject_scans = [scan for scan in files if subject in scan]
    subj_ratings = db.session.query(ScanRater.scan_type, ScanRater.scene, db.func.count()).filter_by(subj_name=subject).\
        group_by(ScanRater.scan_type, ScanRater.scene).all()

    # sanity check for printing the scans
    for scan_type, scene, count in subj_ratings:
        print(scan_type, scene, count)

    return render_template('subject_scan.html', subject=subject, subject_scans=subject_scans, scan_ratings=subj_ratings)

# FIXED
@app.route('/scan_rater/<subject>/<filename>', methods=['GET', 'POST'])
@login_required
def scan_rater(subject, filename):
    # Remove the file ending to just get the DBSeries_desc
    scan = filename[filename.find('R_')+2 : filename.find('.fM')]
    
    # Add scene to the database
    scene = 0
    if 'scene1' in filename:
        scene = 1
    elif 'scene2' in filename:
        scene = 2
    scan_ratings = db.session.query(ScanRater).filter_by(subj_name=subject, scan_type=scan, scene=scene)
    form = ImgRating()
    if form.validate_on_submit():
        user = Usernames.query.filter_by(username=current_user.username).first_or_404()
        scan_rating = ScanRater(subj_name=subject, scan_type=scan, rating=form.rating.data, 
                                distort_notes=form.distort_okay.data, SBF_corr_notes=form.SBF_corruption.data,
                                full_brain_notes=form.full_brain_coverage.data, CIFTI_notes = form.CIFTI_map_typ.data,
                                dropout_notes=form.dropout.data, notes=form.notes.data, scan_rater=user, scene=scene)
        db.session.add(scan_rating)
        db.session.commit()
        flash('Thanks for rating!')
        return redirect(url_for('scan_rater', subject=subject, filename=filename))
    return render_template('rate_image.html', image_ratings=scan_ratings, form=form, filename=filename, subject=subject, scan=scan, scene=scene)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Goodbye, we will miss you!")
    return redirect(url_for('home_page'))