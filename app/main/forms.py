from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required, Length

class DisplayForm(Form):
    string = StringField('Nickname or Email to display', validators=[Required(), Length(1, 64)])
    submit = SubmitField('Get Locations')
