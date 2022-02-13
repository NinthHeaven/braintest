# Forms (such as login, register, etc.)
# These will be passed into the server as a "POST" request
# These variables should NOT be confused to their database counterparts 
# They are the precursor to what goes into the database

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, SelectField, RadioField
from wtforms.validators import DataRequired, EqualTo, ValidationError, Length, InputRequired, NumberRange
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app.models import Usernames

# Login form data
class Login(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# Register data 
class Register(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    re_password = PasswordField('Enter password again', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        # Make sure username doesn't exist already
        user = Usernames.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Username already exists.')

# Edit profile form (that will be deleted later)
class EditProfile(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfile, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = Usernames.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('This username is already taken.')

# AKA the Scan Rater. Named it differently because I did not want similar sounding classes
class ImgRating(FlaskForm):
    #username = StringField('Username', validators=[DataRequired()])
    distort_okay = SelectField('Is distortion correction ok? (i.e., does the location of the gray/white matter transition in the fMRI (SBRef) image align nicely with the white matter surface (green) outline?). If not, please elaborate.',
                               choices=[(None, 'Select an option'), ('yes', 'Yes'), ('no', 'No')], default=None, validators=[DataRequired()])
    SBF_corruption = SelectField('Is there SBRef corruption? (i.e., any artifacts that look abnormal, e.g., dark lines across SBRef indicate slice “dropout” due to motion?). If so, please elaborate.',
                                 choices=[(None, 'Select an option'), ('yes', 'Yes'), ('no', 'No')], default=None, validators=[DataRequired()])
    full_brain_coverage = SelectField('Is there full brain coverage? (I.e., is all of the brain, including the cerebellum, captured within the “final fMRI mask” (fuchsia) outline? In “scene 2”, this will be clear with areas where the cyan outline is present, but surrounding nothing, indicating regions where the SBRef has been masked by the “final fMRI mask”. Quantify % of missing brain region to nearest 20%; if less than 10% missing, call it “0%”; if 90% or more missing, call it “100%". If not, please elaborate.',
                                      choices=[(None, 'Select an option'), ('yes', 'Yes'), ('no', 'No')], default=None, validators=[DataRequired()])
    CIFTI_map_typ = SelectField('Does mapping of CIFTI onto surface/volume look “reasonable/typical”? If not, please elaborate.',
                                choices=[(None, 'Select an option'), ('yes', 'Yes'), ('no', 'No')], default=None, validators=[DataRequired()])
    dropout = SelectField('Is there abnormal dropout (i.e., dark areas within fuchsia outline)? (Some T2* dropout is expected and varies in location between AP/PA scans and by subject. Typical T2* dropout is L/R symmetric and common in anterior frontal and temporal lobes.) If abnormal dropout, please elaborate.',
                          choices=[(None, 'Select an option'), ('yes', 'Yes'), ('no', 'No')], default=None, validators=[DataRequired()])
    notes = StringField('Any additional notes about the scan?')
    rating = RadioField('Quality Rating?', choices=[('good', '0 (Good)'), ('okay', '1 (Okay)'), ('bad', '2 (Bad)'), ('severe', '3 (Severe)')])
    
    # These are the additional notes for when a distortion problem is noted
    distort_notes = StringField('Please elaborate below')
    SBF_notes = StringField('Please elaborate below')
    full_brain_notes = StringField('Please elaborate below')
    CIFTI_notes = StringField('Please elaborate below')
    dropout_notes = StringField('Please elaborate below')


    submit = SubmitField('Submit Rating')

# Was originally used to switching which scene to display
# Perhaps will be updated later once my JS ability catch up
class SceneChoose(FlaskForm):
    scene = SelectField('Select Scene', choices=[('both', 'Both'), ('one', '1'), ('two', '2')])

# This is for broadcasts
class Notifications(FlaskForm):
    notif = TextAreaField('Message', validators=[DataRequired()])
    submit = SubmitField('Broadcast message')