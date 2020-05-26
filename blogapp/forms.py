from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, ValidationError
from wtforms.validators import DataRequired, Length, Email, EqualTo
from blogapp import mongo

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=5, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Submit')

    def validate_username(self, username):
        users = mongo.db.users
        user = users.find_one({'username': username.data})
        if user:
            raise ValidationError('This username is already taken. Please choose another one.')
    
    def validate_email(self, email):
        users = mongo.db.users
        user = users.find_one({'email': email.data})
        if user:
            raise ValidationError('An account with that email is already registered.')

class LoginForm(FlaskForm):
    email = StringField('Email: ', validators=[Email()])
    password = PasswordField('Password: ', validators=[DataRequired()])
    remember = BooleanField('Remember me')
    submit = SubmitField('Submit')