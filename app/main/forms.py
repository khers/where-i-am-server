from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, DecimalField, SelectField
from wtforms.ext.dateutil.fields import DateTimeField
from wtforms.validators import Required, Length, NumberRange

COUNT = [(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')]

class DisplayForm(Form):
    target = SelectField('User to display', coerce=int)
    count = SelectField('How much location history to display', coerce=int, choices=COUNT, default=1)
    submit = SubmitField('Get Locations')

class LocationForm(Form):
    latitude = DecimalField('Latitude', places=None, validators=[Required(), NumberRange(min=-90, max=90)])
    longitude = DecimalField('Longitude', places=None, validators=[Required(), NumberRange(min=-180, max=180)])
    when = DateTimeField('When (should be in UTC)', validators=[])
    submit = SubmitField('Save Location')
