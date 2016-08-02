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
    inithour = SelectField("Initial Hour", validators=[DataRequired()],
                choices=[('01','01'),
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
