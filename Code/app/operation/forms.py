from flask_wtf import FlaskForm
from wtforms import (StringField,
                     PasswordField,
                     SubmitField,
                     SelectField,
                     ValidationError,
                     )
from wtforms.validators import (DataRequired,
                                Length,
                                EqualTo,
                                Email,
                                Regexp,
                                )
from flask_wtf.file import FileField

from ..models.Roleomg import Role
from ..models.User import User


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('', validators=[DataRequired()])
    password1 = PasswordField('', validators=[
        DataRequired(), Length(6, 15)])

    password2 = PasswordField('', validators=[
        DataRequired(),
        EqualTo('password1', message='Passwords must match')])
    submit = SubmitField('Update Password')


class EditForm(FlaskForm):
    name = StringField('Username', validators=[
        DataRequired(), Length(4, 64)])
    location = StringField('Location', validators=[Length(0, 64)])
    submit = SubmitField('submit')


class ChangeAvatars(FlaskForm):
    avatar = FileField('')
    submit = SubmitField('submit')


class EditProfileAdminForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64),
                                             Email()])
    username = StringField('User', validators=[
        DataRequired(), Length(1, 64),
        Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
               'Usernames must have only letters, numbers, dots or '
               'underscores')])
    role = SelectField('Role', coerce=int)
    location = StringField('Location', validators=[Length(0, 64)])
    submit = SubmitField('Submit')

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already in use.')




