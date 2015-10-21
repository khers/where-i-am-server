from flask.ext.wtf import Form
from wtforms import StringField, SubmitField, DecimalField
from wtforms.ext.dateutil.fields import DateTimeField
from wtforms.validators import Required, Length, NumberRange

class DisplayForm(Form):
    string = StringField('Nickname or Email to display', validators=[Required(), Length(1, 64)])
    submit = SubmitField('Get Locations')

class LocationForm(Form):
    latitude = DecimalField('Latitude', places=None, validators=[Required(), NumberRange(min=-90, max=90)])
    longitude = DecimalField('Longitude', places=None, validators=[Required(), NumberRange(min=-180, max=180)])
    when = DateTimeField('When (should be in UTC)', validators=[])
    submit = SubmitField('Save Location')
