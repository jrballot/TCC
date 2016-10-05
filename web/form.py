#
# Form Validator

from flask_wtf import Form
from wtforms import StringField, DateField, IntegerField, FloatField, SelectField, PasswordField, RadioField
from wtforms.validators import DataRequired, Length, EqualTo



class RegisterForm(Form):
    name = StringField(
        'Username',
        validators=[DataRequired(), Length(min=4, max=25)]
    )

    email = StringField(
        'Email',
        validators=[DataRequired(), Length(min=6, max=40)]
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired(), Length(min=6, max=40)]
    )

    confirm = PasswordField(
        "Repeat Password",
        validators=[DataRequired(), EqualTo('password', message='Passwords must match')]
    )

class LoginForm(Form):
    name = StringField(
        'Username',
        validators=[DataRequired()]
    )

    password = PasswordField(
        'Password',
        validators=[DataRequired()]
    )



class ModelForm(Form):
    expnme = StringField('Experiment Name',validators=[DataRequired()])

    timmax = SelectField('Time of Simulation',
                validators=[DataRequired()], choices=[('06','06'),('12','12'),('18','18'),('24','24')])

    timeunit = SelectField('Time Unit',
                validators=[DataRequired()],
                choices=[('h','hour'),('m','minute'),('s','second'),('d','days')])

    deltaXY = RadioField('Distance in X and Y', choices=[('30000','30000 metters')])
    nnXYp = RadioField('Pointes per Area in X and Y', choices=[('60','60 points')])

    centlat = FloatField("Center Latitude", validators=[DataRequired()])
    centlon = FloatField("Center Longitude", validators=[DataRequired()])

    #inttime = IntegerField("Integration Time", validators=[DataRequired()])
    initdate = DateField(
                "Initial Date (mm/dd/yyyy)",
                validators=[DataRequired()],
                format='%m/%d/%Y')
    inithour = SelectField("Initial Hour", validators=[DataRequired()],
                choices=[('00','00'),('01','01'),
                        ('02','02'), ('03','03'),
                        ('04','04'), ('05','05'),
                        ('06','06'), ('07','07'),
                        ('08','08'), ('09','09'),
                        ('10','10'), ('11','11'),
                        ('13','12'), ('13','13'),
                        ('14','14'), ('15','15'),
                        ('16','16'), ('17','17'),
                        ('18','18'), ('19','19'),
                        ('20','20'), ('21','21'),
                        ('22','22'), ('21','23') ])

    initminute = SelectField("Initial Minute", validators=[DataRequired()],
                    choices=[
                    ('00','00'),
                    ('01','01'),
                    ('02','02'),
                    ('03','03'),
                    ('04','04'),
                    ('05','05'),
                    ('06','06'),
                    ('07','07'),
                    ('08','08'),
                    ('09','09'),
                    ('10','10'),
                    ('11','11'),
                    ('12','12'),
                    ('13','13'),
                    ('14','14'),
                    ('15','15'),
                    ('16','16'),
                    ('17','17'),
                    ('18','18'),
                    ('19','19'),
                    ('20','20'),
                    ('21','21'),
                    ('22','22'),
                    ('23','23'),
                    ('24','24'),
                    ('25','25'),
                    ('26','26'),
                    ('27','27'),
                    ('28','28'),
                    ('29','29'),
                    ('30','30'),
                    ('31','31'),
                    ('32','32'),
                    ('33','33'),
                    ('34','34'),
                    ('35','35'),
                    ('36','36'),
                    ('37','37'),
                    ('38','38'),
                    ('39','39'),
                    ('40','40'),
                    ('41','41'),
                    ('42','42'),
                    ('43','43'),
                    ('44','44'),
                    ('45','45'),
                    ('46','46'),
                    ('47','47'),
                    ('48','48'),
                    ('49','49'),
                    ('50','50'),
                    ('51','51'),
                    ('52','52'),
                    ('53','53'),
                    ('54','54'),
                    ('55','55'),
                    ('56','56'),
                    ('57','57'),
                    ('58','58')])
