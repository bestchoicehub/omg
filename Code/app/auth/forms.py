from wtforms import ValidationError
from ..models.User import User
# from utils import log
from flask_wtf import FlaskForm
from wtforms import (StringField,
                     PasswordField,
                     BooleanField,
                     SubmitField, )
from wtforms.validators import (DataRequired,
                                Length,
                                Email,
                                Regexp,
                                EqualTo, )


# Web Form
# StringField, PasswordField, BooleanField, SubmitField

class LoginForm(FlaskForm):
    # validators=[the requirements need to satisfy]
    # DataRequired（）must input
    # email: the input should be email format(@)
    email = StringField('', validators=[DataRequired(), Length(1, 64),
                                        Email()], render_kw={"placeholder": "Email Address"})
    password = PasswordField('', validators=[DataRequired()], render_kw={"placeholder": "Password"})
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('log In')


class RegistrationForm(FlaskForm):
    email = StringField('', validators=[DataRequired(), Length(1, 64),
                                        Email()])
    username = StringField('', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    password = PasswordField('', validators=[
        DataRequired(), Length(6, 15),
        Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{6,}', 0,
               'Passwords must contain: a minimum of 1 lower case letter, a minimum of 1 upper case letter, '
               'a minimum of 1 numeric character, a minimum of 1 special character ')])
    password2 = PasswordField('', validators=[DataRequired(),
                                              EqualTo('password', message='Passwords must match.')])
    submit = SubmitField('Register')

    def validate_email(self, field):
        # User.query - BaseQuery object
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered, please use another email')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use. please use another name', )


class PasswordResetRequestForm(FlaskForm):
    email = StringField('', validators=[DataRequired(), Length(1, 64),
                                        Email()], render_kw={"placeholder": "Email Address"})
    submit = SubmitField('Reset')


class PasswordResetForm(FlaskForm):
    new_password1 = PasswordField('', validators=[
        DataRequired(), Length(6, 15),
        Regexp('^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[$@$!%*?&])[A-Za-z\d$@$!%*?&]{6,}', 0,
               'The password must include at least 1 uppercase letter, '
               '1 lowercase letter, 1 numbers and 1 special character.')])

    new_password2 = PasswordField('', validators=[DataRequired(),
                                                  EqualTo('new_password1', message='Passwords must match.')])
    submit = SubmitField('reset')
