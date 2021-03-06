from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectMultipleField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User, ReadPermission

class LoginForm(Form):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    password = PasswordField('Password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log In')

class RegistrationForm(Form):
    email = StringField('Email', validators=[Required(), Length(1,64), Email()])
    nickname = StringField('Display Name', validators=[Required(), Length(1,64),
                        Regexp('^[A-Za-z0-9_.]*$', 0, "Display names must have only letters, numbers, dots, or underscores")])
    password = PasswordField('Password', validators=[Required(), EqualTo('password2', message='Passwords must match.')])
    password2 = PasswordField('Confirm Password', validators=[Required(), EqualTo('password2', message='Passwords must match.')])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_nickname(self, field):
        if User.query.filter_by(nickname=field.data).first():
            raise ValidationError('Display name alread in use.')

class ChangePasswordForm(Form):
    old_password = PasswordField('Old password', validators=[Required()])
    password = PasswordField('New password', validators=[
        Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm new password', validators=[Required()])
    submit = SubmitField('Update Password')

class PasswordResetRequestForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    submit = SubmitField('Reset Password')

class PasswordResetForm(Form):
    email = StringField('Email', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('New Password', validators=[
        Required(), EqualTo('password2', message='Passwords must match')])
    password2 = PasswordField('Confirm password', validators=[Required()])
    submit = SubmitField('Reset Password')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError('Unknown email address.')

class ChangeEmailForm(Form):
    email = StringField('New Email', validators=[Required(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[Required()])
    submit = SubmitField('Update Email Address')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

class DeleteLocationsForm(Form):
    locations = SelectMultipleField('Your location data', coerce=int)
    confirm = BooleanField("I'm really sure")
    submit = SubmitField('Delete Selected Locations')

    def validate_locations(self, field):
        loc_ids = set(field.data)
        if len(loc_ids) == 0:
            raise ValidationError('Not locations selected')
        if -1 in loc_ids and len(loc_ids) > 1:
            raise ValidationError('Cannot select locations and All')

class PermissionsForm(Form):
    available = SelectMultipleField('Users that cannot read your location data',
                                    coerce=int)
    can_read = SelectMultipleField('Users who can read your location data',
                                   coerce=int)
    submit = SubmitField('Update Permissions')
