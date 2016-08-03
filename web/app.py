from form import modelFormValidator


from flask import Flask, render_template, session, url_for, flash, redirect, request, g
from functools import wraps
from string import Template
import subprocess

import os

# change Template delimiter
class MyTemplate(Template):
    delimiter = "@"
    #idpattern = r'[_a-z][a-z0-9]'



app = Flask(__name__)
app.config.from_object('_config')
#GoogleMaps(app)

@app.route("/", methods=['GET'])
def root():
    return render_template('index.html')


## About page
#
@app.route("/about", methods=['GET'])
def about():
    return render_template("about.html")

## Run Models Page
#
@app.route("/confmodels", methods=['GET','POST'])
def confmodels():
    error = None
    form = modelFormValidator(request.form)
    if request.method == 'POST' and form.validate():



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
            form=modelFormValidator(request.form))

@app.route("/runmodels", methods=['GET','POST'])
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

    return render_template('runmodels.html', error=error, input_data=inputdata_dict, result=stdout)

if __name__ == "__main__":
    app.run(debug=True)
