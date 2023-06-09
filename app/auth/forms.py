from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User

# Übernommen aus den Beispielen von Miguel Grinberg
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

# Übernommen aus den Beispielen von Miguel Grinberg
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email(), Length(min=4, max=120)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=128)])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(), EqualTo('password'), Length(min=8, max=128)])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')
        
# Übernommen aus den Beispielen von Miguel Grinberg
class ResetPasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8, max=128)])
    confirm_password = PasswordField(
        'Confirm New Password', validators=[DataRequired(), EqualTo('new_password', message='Passwords must match'), Length(min=8, max=128)])
    submit = SubmitField('Reset Password')
    