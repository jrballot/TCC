#
# Form Validator

from flask_wtf import Form
from wtforms import StringField, DateField, IntegerField, FloatField, SelectField
from wtforms.validators import DataRequired



class modelFormValidator(Form):
    expnme = StringField('Experiment Name',validators=[DataRequired()])

    timmax = IntegerField('Time of Simulation',
                validators=[DataRequired()])

    timeunit = SelectField('Time Unit',
                validators=[DataRequired()],
                choices=[('h','hour'),('m','minute'),('s','second')])

    deltax = IntegerField("Distance on X ", validators=[DataRequired()])
    deltay = IntegerField("Distance on Y ", validators=[DataRequired()])
    nnxp = IntegerField("Points per Area in X", validators=[DataRequired()])
    nnyp = IntegerField("Points per Area in Y", validators=[DataRequired()])
    centlat = FloatField("Center Latitude", validators=[DataRequired()])
    centlon = FloatField("Center Longitude", validators=[DataRequired()])

    inttime = IntegerField("Integration Time", validators=[DataRequired()])
    initdate = DateField(
                "Initial Date (mm/dd/yyyy)",
                validators=[DataRequired()],
                format='%m/%d/%Y')
    inithour = IntegerField("Initial Hour", validators=[DataRequired()])
    initminute = IntegerField("Initial Minute", validators=[DataRequired()])
