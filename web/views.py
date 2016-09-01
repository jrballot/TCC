

## IMPORTS

from form import ModelForm, LoginForm, RegisterForm

from flask import Flask, render_template, session, url_for, flash, redirect, request, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from string import Template
import models
import subprocess

import os

# change Template delimiter
class MyTemplate(Template):
    delimiter = "@"
    #idpattern = r'[_a-z][a-z0-9]'



app = Flask(__name__)
app.config.from_object('_config')
db = SQLAlchemy(app)



## Helper functions
def login_required(test):
    @wraps(test)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return test(*args, **kwargs)
        else:
            flash('You need to login first.')
            return redirect(url_for('login'))
    return wrap


## Route page
@app.route("/", methods=['GET','POST'])
def login():
    error = None
    form = LoginForm(request.form)
    if request.method == 'POST':
        if form.validate_on_submit():
            user = models.User.query.filter_by(name=request.form['name']).first()
            if user is not None and user.password == request.form['password']:
                session['logged_in'] = True
                session['name'] = user.name
                flash("Welcome!")
                return redirect(url_for('confmodels'))
            else:
                error = 'Invalid username or password.'
        else:
            error = 'Both fields arer requerid.'

    return render_template('login.html', form=form, error=error)

@app.route('/logout')
def logout():
    session.pop("logged_in", None)
    session.pop("name", None)

    flash("You ware logged out")
    return redirect(url_for('login'))

## Register page
#
@app.route('/register/',methods=['GET','POST'])
def register():
    error = None
    form = RegisterForm(request.form)
    if request.method == 'POST':

        if form.validate_on_submit():

            new_user = models.User(
                form.name.data,
                form.email.data,
                form.password.data,
            )

            db.session.add(new_user)
            db.session.commit()
            flash('Thanks for registering at BAS. Please login.')
            return redirect(url_for('login'))
    return render_template('register.html', form=form, error=error)


## About page
#
@app.route("/about", methods=['GET'])
@login_required
def about():
    return render_template("about.html")

## Run Models Page
#
@app.route("/confmodels", methods=['GET','POST'])
@login_required
def confmodels():
    error = None
    form = ModelForm(request.form)
    if request.method == 'POST' and form.validate():

        ## sava conf to database with the user_id
        new_model = Model(
            form.expnme.data,
            form.timmax.data,
            form.timeunit.data,
            form.inittime.data,
            form.deltax.data,
            datetime.datime.strptime(form.initdate.data,"%d/%m/%y"),
            form.deltay.data,
            form.nnxp.data,
            form.nnyp.data,
            form.centlat.data,
            form.centlon.data,

            form.initdate.data.year,
        )
        with open(os.path.join('./','RAMSIN.template'),'r') as f:
            lines = f.readlines()


        mylist = map(lambda each:each.strip('\n'), lines)

        new_lines = []

        if form.initdate.data.month < 10 :
            month = '0'+ str(form.initdate.data.month)

        else:
            month =  form.initdate.data.month

        if form.initdate.data.day < 10 :
            day = '0'+ str(form.initdate.data.day)
        else:
            day =  form.initdate.data.day


        for i in mylist:
            s = MyTemplate(i)
            new_lines.append(s.substitute(
                EXPNME = form.expnme.data,
                TIMMAX = form.timmax.data,
                TIMEUNIT = form.timeunit.data,
                DELTAX = form.deltax.data,
                DELTAY = form.deltay.data,
                NNXP = form.nnxp.data,
                NNYP = form.nnyp.data,
                CENTLAT = form.centlat.data,
                CENTLON = form.centlon.data,
                IMONTH = month,
                IDATE1 = day,
                IYEAR = form.initdate.data.year,
                ITIME1 = str(form.inithour.data)+str(form.initminute.data)))


        formitems = dict(
                        EXPNME = form.expnme.data,
                        TIMMAX = form.timmax.data,
                        TIMEUNIT = form.timeunit.data,
                        DELTAX = form.deltax.data,
                        DELTAY = form.deltay.data,
                        NNXP = form.nnxp.data,
                        NNYP = form.nnyp.data,
                        CENTLAT = form.centlat.data,
                        CENTLON = form.centlon.data,
                        IMONTH = month,
                        IDATE1 = day,
                        IYEAR = form.initdate.data.year,
                        ITIME1 = str(form.inithour.data)+str(form.initminute.data))

        with open(os.path.join('./tmp','input.data'),'w') as f:
            for key, value in formitems.items():
                f.write(key + " = " + str(value) + "\n")


        with open(os.path.join('./tmp','RAMSIN'),'w') as f:
            for line in new_lines:
                f.write(line)
                f.write('\n')

    return render_template("confmodels.html", error=error,
            form=ModelForm(request.form), username = session['name'])

@app.route("/runmodels", methods=['GET','POST'])
@login_required
def runmodels():
    error = None
    inputdata_dict = None
    stdout = None
    stderr = None

    # execute brams
    if request.method == "POST":
        process = subprocess.Popen(['python','../brams/bras.py','./tmp/RAMSIN'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

    # read last configuration
    if os.path.isfile(os.path.join('./tmp', 'input.data')):

        with open(os.path.join('./tmp', 'input.data'), 'r') as f:
            idxdata = f.readlines()

        idxdata = map(lambda each: each.strip('\n'), idxdata)

        inputdata_dict = {}
        for item in idxdata:
            tmp_dict = dict(x.split('=') for x in item.split(','))
            for k, v in tmp_dict.items():
                inputdata_dict[k.strip()] = v.strip()

    else:
        error = "File input.data dosen't exist"

    return render_template('runmodels.html', error=error, input_data=inputdata_dict, result=stdout, username=session['name'])


@app.route("/home", methods=['GET'])
@login_required
def home():
    return render_template('home.html')

if __name__ == "__main__":
    app.run(debug=True)
