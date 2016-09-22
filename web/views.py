## IMPORTS

from form import ModelForm, LoginForm, RegisterForm

from flask import Flask, render_template, session, url_for, flash, redirect, request, g, jsonify
from flask_sqlalchemy import SQLAlchemy
from functools import wraps
from string import Template
from datetime import datetime
import subprocess

import os

# change Template delimiter
class MyTemplate(Template):
    delimiter = "@"
    #idpattern = r'[_a-z][a-z0-9]'



app = Flask(__name__)
app.config.from_object('_config')
db = SQLAlchemy(app)

import models

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
                session['user_id'] = user.id
                flash("Welcome!")
                return redirect(url_for('home'))
            else:
                error = 'Invalid username or password.'
        else:
            error = 'Both fields arer requerid.'

    return render_template('login.html', form=form, error=error)

@app.route('/logout')
def logout():
    session.pop("logged_in", None)
    session.pop("name", None)
    session.pop('user_id', None)

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
    return render_template("about.html", username=session['name'])

## Run Models Page
#
@app.route("/confmodels", methods=['GET','POST'])
@login_required
def confmodels():
    error = None
    form = ModelForm(request.form)
    if request.method == 'POST' and form.validate():

        ## sava conf to database with the user_id
        new_model = models.Model(
            form.expnme.data,
            form.timmax.data,
            form.timeunit.data,
            form.inttime.data,
            form.initdate.data,
            form.inithour.data,
            form.initminute.data,
            form.centlat.data,
            form.centlon.data,
            form.nnXYp.data,
            form.deltaXY.data,
            session['user_id']
        )

        db.session.add(new_model)
        db.session.commit()
        return redirect(url_for('allmodels'))

    return render_template("confmodels.html", error=error,
            form=ModelForm(request.form), username = session['name'])

def getModels(userid):
    return db.session.query(models.Model).filter_by(user_id=userid).order_by(models.Model.id.desc())

## Configure RAMSIN.template with especified model
# This will create 3 files:
#       RAMSIN_MAKESFC      ->  create surface
#       RAMSIN_MAKEVFILE    ->  create virtual files
#       RAMSIN_INITIAL      ->  run model
#
def configure_ramsin(model):

    with open(os.path.join(os.path.abspath(os.path.dirname(__file__)),'RAMSIN.template'),'r') as f:
        lines = f.readlines()

    mylist = map(lambda each:each.strip('\n'), lines)

    new_lines = []

    ## correct month format
    if model.initial_date.month < 10 :
        month = '0'+ str(model.initial_date.month)
    else:
        month =  model.initial_date.month

    ## correct day format
    if model.initial_date.day < 10 :
        day = '0'+ str(model.initial_date.day)
    else:
        day =  model.initial_date.day

    ## correct hour format
    if model.initial_hour_hour < 10 :
        hour = '0'+ str(model.initial_hour_hour)
    else:
        hour =  model.initial_hour_hour

    ## correct minute format
    if model.initial_hour_minute < 10 :
        minute = '0'+ str(model.initial_hour_minute)
    else:
        minute =  model.initial_hour_minute

    for runtype in ['MAKESFC','MAKEVFILE','INITIAL']:
        for i in mylist:
            s = MyTemplate(i)
            new_lines.append(
                s.substitute(
                    EXPNME = model.exp_name,
                    RUNTYPE = runtype,
                    TIMMAX = model.time_simulation,
                    TIMEUNIT = model.time_simulation_unit,
                    DELTAX = model.distance_x_y,
                    DELTAY = model.distance_x_y,
                    NNXP = model.number_points_x_y,
                    NNYP = model.number_points_x_y,
                    CENTLAT = model.center_point_latitude,
                    CENTLON = model.center_point_longitude,
                    IMONTH = month,
                    IDATE1 = day,
                    IYEAR = model.initial_date.year,
                    ITIME1 = str(hour)+str(minute)
                )
            )

        with open(os.path.join(os.path.abspath('./tmp'),'RAMSIN_'+runtype),'w') as f:
            for line in new_lines:
                f.write(line)
                f.write('\n')

        ## Clear new_lines for nex runtype
        del new_lines[:]


## Run a model configuration
#
@app.route("/run_model/<int:model_id>")
@login_required
def run_model(model_id):
    error=None
    model = db.session.query(models.Model).filter_by(id=model_id).first()
    configure_ramsin(model)

    initial_date = str(model.initial_date).replace('-','')

    if model.initial_hour_hour >= 10:
        initial_hour_hour = str(model.initial_hour_hour)
    else:
        initial_hour_hour = '0' + str(model.initial_hour_hour)

    try:
        ## run brams.py pass data model
        flash('Executing model id {}. It may take awhile.'.format(model_id))

        ## using subprocess to rund brams.py
        subprocess.call([os.path.abspath('./brams/bras.py'),
                        '--date', initial_date,
                        '--time', initial_hour_hour])

    except Exception as exception:
        error="Somenting goes wrong: " + str(exception)

        print error
        print str(model.initial_date).replace('-','')
        print '0' + str(model.initial_hour_hour)

    return redirect(url_for('allmodels'))


## Delete a model configuration
#
@app.route("/delete_model/<int:model_id>")
@login_required
def delete_model(model_id):
    model = db.session.query(models.Model).filter_by(id=model_id)
    model.delete()
    db.session.commit()
    flash('Model id {} was deleted.'.format(model_id))
    return redirect(url_for('allmodels'))
    pass


@app.route("/allmodels", methods=['GET','POST'])
@login_required
def allmodels():
    error = None
    inputdata_dict = None
    stdout = None
    stderr = None

    if request.method == "POST":
        pass

    return render_template('allmodels.html', error=error, models=getModels(session['user_id']), result=stdout, username=session['name'])


@app.route("/home", methods=['GET'])
@login_required
def home():
    return render_template('home.html', username=session['name'])


if __name__ == "__main__":
    app.run(debug=True)
