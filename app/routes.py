from flask import render_template, redirect, url_for, request, flash, send_from_directory
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.sql.elements import Null, TextClause
from werkzeug.urls import url_parse
from werkzeug.utils import send_file
#from werkzeug.utils import secure_filename
from app import app, db
from app.forms import ImgRating, Login, Register, EditProfile, Notifications, SceneChoose
from app.models import Usernames, Broadcasts, ScanRater
from datetime import datetime
import os
from flask import send_file

# Static folder directory where all scans will be scanned and uploaded to app
dir = 'app/static/subjects/HCD_wb1.4.2.pngs'

# Listing all the files inside 
files = os.listdir(dir)

# Constantly update the time a user accesses the page
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# Home page directory
@app.route("/")
@login_required
def home_page():
    # Create a temporary database connection
    users = db.session.query(Usernames).all()

    # Display number of subjects currently in the database
    total_subjects = set()
    # Get a list of the subjects and also the scan types (will be used for accessing other scans)
    for i in files:
        if i not in total_subjects:
            total_subjects.add(i.split('_V1_MR', 1)[0])

    total_subjects = len(total_subjects)


    # Display number of scans that have been rated / total (look at scan_rater for demo)
    total_scans = 0
    for file in files:
        total_scans += 1

    # Display number of scans rated (that are in the database)
    scans_rated = db.session.query(ScanRater).distinct(ScanRater.subj_name).count()

    # Display number of scans per user (leaderboard, like mind control)
    # Same code for profile, copied and pasted below
    user_ratings = db.session.query(Usernames.username, db.func.count(Usernames.id)).\
        join(Usernames.scan_ratings).group_by(Usernames.id).all()

    user_ratings = {user:num for user,num in user_ratings}

    # Display ratings in reverse order
    leaderboard = {user:num for user,num in sorted(user_ratings.items(), key=lambda item: item[1], reverse=True)}
    #print(leaderboard)

    # % of scans rated Good, Bad, Poor, etc..
    scan_stats = db.session.query(ScanRater.rating, db.func.count()).group_by(ScanRater.rating).all()

    scan_stats = {rating:count for rating,count in scan_stats}

    # Anything else?
    # to be continued...

    return render_template('home.html', users=users, total_subjects=total_subjects, leaderboard=leaderboard, total_scans=total_scans, scan_stats=scan_stats, rated_scans=scans_rated)

# login page
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

# Register page (will redirect if user exists)
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
# Profile page (currently only accessible to admin)
@app.route('/user/<username>', methods=['GET', 'POST'])
@login_required
def user(username):

    # This is mainly for announcements (which currently only appear on profile page)
    # TODO: delete if no use is found for this feature..
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

    # returns a tuple of ratings per user (BrainBot, 1; admin, 1)
    user_ratings = db.session.query(Usernames.username, db.func.count(Usernames.id)).\
        join(Usernames.scan_ratings).group_by(Usernames.id).all()

    user_ratings = {user:num for user,num in user_ratings}

    # Summary of ratings for users
    ratings_summary = db.session.query(ScanRater)

    return render_template('user.html', user=user, announcements=announcements, form=form, user_ratings=user_ratings, ratings_summary=ratings_summary)

# TODO: delete later...
# Edit profile feature (was for earlier testing)
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

# Update changes and overall test hug
# TODO: make this only accessible to select users to try different implementation of features
@app.route('/logs')
@login_required
def logs():
    return render_template('logs.html')


# TODO: WORK ON THESE NEXT THREEE FUNCTIONS
# TODO: DELETE SCENE FROM MODELS
# TODO: RATER AND RATE_SCAN FUNCTIONS


# THIS WILL BE NEW RATER FUNC, DELETE ANY DUPLICATES
@app.route('/rater', methods=['GET', 'POST'])
@login_required
def rater():
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

    subject_ratings = {subject:count for subject,count in total_ratings}

    ## NOTE: Remember that the ratings have already been made by someone else (talk about how to analyze ratings)


    return render_template('rater.html', subj_list=subj_list, total_ratings=subject_ratings, total_files=total_files, subject_files=subject_files)

@app.route('/subject/<subject>', methods=['GET', 'POST'])
@login_required
def subject_scans(subject):
    # Redundant line of code (probably will fix later)
    subj_ratings = db.session.query(ScanRater.scan_type, db.func.count()).filter_by(subj_name=subject).\
        group_by(ScanRater.scan_type).all()

    # Depict scan names (to fix the rater page)
    scan_names = set()

    # List files appropriately
    for file in files:
        if subject in file:
            scan_names.add(file[file.find('R_')+2 : file.find('.fM')])



    return render_template('subject_scan.html', subject=subject, scans=scan_names, scan_ratings=subj_ratings)

# Actual scan rater page
# TODO: Implement some stylistic changes to this page
@app.route('/scan_rater/<subject>/<filename>', methods=['GET', 'POST'])
@login_required
def scan_rater(subject, filename):
    # Remove the file ending to just get the DBSeries_desc
    scan = filename
   
    
    images = []
    for file in files:
        if subject in file and scan in file:
            images.append(file)

   
    # Add scene to the database
    scene = 0
    if 'scene1' in filename:
        scene = 1
    elif 'scene2' in filename:
        scene = 2
    scan_ratings = db.session.query(ScanRater).filter_by(subj_name=subject, scan_type=scan)
    form = ImgRating()
    scene_form = SceneChoose()
    if form.validate_on_submit():
        user = Usernames.query.filter_by(username=current_user.username).first_or_404()
        scan_rating = ScanRater(subj_name=subject, scan_type=scan, rating=form.rating.data, distort_okay=form.distort_okay.data,
                                distort_notes=form.distort_notes.data, SBF_corr=form.SBF_corruption.data, SBF_corr_notes=form.SBF_notes.data,
                                full_brain_cov=form.full_brain_coverage.data, full_brain_notes=form.full_brain_notes.data, 
                                CIFTI_map=form.CIFTI_map_typ.data, CIFTI_notes = form.CIFTI_notes.data, dropout=form.dropout.data,
                                dropout_notes=form.dropout_notes.data, notes=form.notes.data, scan_rater=user)
        db.session.add(scan_rating)
        db.session.commit()
        flash('Thanks for rating!')
        return redirect(url_for('scan_rater', subject=subject, filename=filename))
    return render_template('rate_image.html', image_ratings=scan_ratings, form=form, filename=filename, subject=subject, scan=scan, scene=scene, scene_form=scene_form, images=images)

# TODO: Add this to home page or separate page
# only accessed by adding '/download' to end of URL (will auto download a file)
# TODO remove the rater (probably associated with ID?)
@app.route('/download')
@login_required
def download():
    import csv 
    with open('app/ratings.csv', 'w') as f:
        # Create a csv file
        csv = csv.writer(f)
        # Get all of the data and add the column names
        # TODO: filter the scan_rater column
        ratings_dat = db.session.query(ScanRater).all()
        columns = ['id', 'subject', 'scan_type', 'distort_okay',
                   'distort_notes', 'SBF_corruption', 'SBF_corr_notes',
                   'full_brain_coverage', 'full_brain_notes', 'CIFTI_map_typical',
                   'CIFTI_notes', 'dropout', 'dropout_notes', 'rating', 'notes']
        csv.writerow(columns)
        # Apply data to file
        [csv.writerow([getattr(curr, column.name) for column in ScanRater.__mapper__.columns]) for curr in ratings_dat]

    # Send the file to user for download
    return send_file('ratings.csv', as_attachment=True)


# Log off
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Goodbye, we will miss you!")
    return redirect(url_for('home_page'))