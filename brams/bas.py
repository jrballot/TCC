#!/usr/bin/env python
import re
import argparse
import os
import shutil
import subprocess
from ftplib import FTP
from pylab import title, savefig
import grads

# file format:  GAMRAMS+data+data[00,06,12,18].(icn|fct).TQ0126L028.(ctl|gmp|grb)
# necessario pegar o primeiro horario do dia seguinte
_pathTMP = os.path.join(os.path.abspath("."),"tmp")
_pathREGIONAL = os.path.join(os.path.abspath("."),"tmp/regional")
_grib2dp = os.path.join(os.path.abspath("."),"grib2dp")
_meteo_only = "/home/jota/meteo-only"
_meteo_only_datain = os.path.join(_meteo_only,"datain/dp-meteo-only")
_pathIMG = os.path.join(os.path.abspath('.'),"output_img")
_pathIMG2 = os.path.join(os.path.abspath('.'),"web/static/img/output_img")

def preRun():

    """
        Validade prerequisits to run the model
    """

    if not os.path.exists(_pathTMP):
        os.makedirs(_pathTMP)

    if not os.path.exists(_pathREGIONAL):
        os.makedirs(_pathREGIONAL)
    else:
        print "Clear {}".format(_pathREGIONAL)
        print "|--> List of files: {}".format(os.listdir(_pathREGIONAL))
        for f in os.listdir(_pathREGIONAL):
            print " |--> removing {} file".format(f)
            os.remove(os.path.join(_pathREGIONAL, f))
        pass

    if not os.path.exists(_pathIMG):
        os.makedirs(_pathIMG)
    
    if not os.path.exists(_pathIMG2):
        os.makedirs(_pathIMG2)


def downloadFiles(fulltime,nextday):


    pattern1 = "GAMRAMS"+fulltime+fulltime[:-2]+"\d\dP.(icn|fct).TQ0126L028.(ctl|gmp|grb)"
    pattern2 = "GAMRAMS"+fulltime+nextday+"\d\dP.(icn|fct).TQ0126L028.(ctl|gmp|grb)"

    #print pattern
    regex1 = re.compile(pattern1)
    regex2 = re.compile(pattern2)

    try:
        ftp = FTP("ftp1.cptec.inpe.br")
        ftp.login()
        ftp.cwd('/modelos/io/tempo/global/T126L28/'+fulltime)
        print "List of files: \n"
        ftpFiles = ftp.nlst()
        for ftpFile in ftpFiles:

            # try something to not re-download all the files

            if re.search(regex1, ftpFile) or re.search(regex2, ftpFile):
                print "Found match: {}".format(ftpFile)
                if not os.path.exists(os.path.join(_pathREGIONAL,ftpFile)):
                    ftp.retrbinary('RETR %s' % ftpFile, open(os.path.join(_pathREGIONAL,ftpFile), "wb").write )
                else:
                    print "File {} already exist".format(ftpFile)


    except Exception as e:
        print "Something goes wrong: {}".format(e)


def grib2dp():
    """
        grib2dp - Will try to covert the global input format from INPE to a DP format needed by BRAMS
    """

    shutil.copy(_grib2dp+"/grbconv.x",_pathREGIONAL+"/grbconv.x")
    shutil.copy(_grib2dp+"/grib2dp.x",_pathREGIONAL+"/grib2dp.x")
    shutil.copy(_grib2dp+"/PREP_IN",_pathREGIONAL+"/PREP_IN")

    try:
        print "Running grib2dp.x ..."
        os.chdir(_pathREGIONAL)
        subprocess.call([_pathREGIONAL+"/grib2dp.x"])
    except Exception as e:
        print "Something goes wrong: {}".format(e)

def copyDP():
    "copyDP - Copy DP files to your proper destination inside BRAMS's hierarchy directories"
    

    patternDP = "dp\d\d\d\d\-\d\d-\d\d-\d\d\d\d"
    regexDP = re.compile(patternDP)

    if os.path.exists(_meteo_only_datain):
      
        try:
            print "Copying DP files"    
            for f in os.listdir(_pathREGIONAL):
                if re.search(regexDP, f):
                    shutil.copy(os.path.join(_pathREGIONAL, f), _meteo_only_datain)
                    print " |--> copying {} to {}".format(f, _meteo_only_datain)
        except Exception as e:
            print "Something goes wrong: {}".format(e)

    else:
        print "No found any DP file"

def runModel():
    """
        runModel - Run BRAMS with a especified RUNTYPE passed by runtype variable.
        Runtype can be one of those:
            INITIAL
            MAKESFC
            MAKEVFILE
    """

    runStages = ['RAMSIN_MAKESFC',"RAMSIN_MAKEVFILE", "RAMSIN_INITIAL"]
    
    commandRunModel = 'mpirun -np 1 ../bin/brams-5.2'

    for runStage in runStages:
        try:
            shutil.copy(os.path.join(_pathTMP, runStage), _meteo_only)
            os.chdir(_meteo_only)
            subprocess.call(['mpirun','-np','1','/home/jota/bin/brams-5.2','-f',runStage])
        except Exception as e:
            print "Something goes wrong: {}".format(e)


def getOutputInPNG(time, date, modelid):
    """
        getOutputInPNG - convert output from BRAMS in a PNG image
    """

    _modelOutputPath = os.path.join(_pathIMG2, modelid)
    
    if not os.path.exists(_modelOutputPath):
        os.makedirs(_modelOutputPath)
    
    year = date[:4]
    month = date[4:6]
    day = date[-2:]
    
    file = os.path.join(_meteo_only,'dataout/POSPROCESS/METEO-ONLY-A-'+year+'-'+month+'-'+day+'-'+time+'0000-g1.ctl')
    ga = grads.GrADS(Window=False)
    fh = ga.open(file)
    
    # Temperatura
    ga.contour(ga.expr('tempk')-274.15)
    title('Temperatura {} dia {}/{}/{} as {}h'.format(fh.title,day,month,year,time))
    savefig(os.path.join(_modelOutputPath,fh.title+'-temperatura-'+date+time+'.png'))
    
    # Precipitacao
    ga.contour('rh')
    title('Precipitacao {} dia {}/{}/{} as {}h'.format(fh.title,day,month,year,time))
    savefig(os.path.join(_modelOutputPath,fh.title+'-precipitacao-'+date+time+'.png'))
    
    pass

def main(date, time, modelid):
    """
        main - it's control the main flow
    """

#    if int(time) < 12:
#        fullData = date+'00'
#    else:
#        fullData = date+'12'
#
    fullData = date+'00'

    nextday = date[:-2] + str(int(date[-2:])+1)
    print "Fulldata: {}".format(fullData)
    print "Next day: {}".format(nextday)

    #preRun()
    #downloadFiles(fullData,nextday)
    #grib2dp()
    #copyDP()
    #runModel()

    getOutputInPNG(time, date, modelid)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BRAS - BRAMS Automation Suit")
    parser.add_argument('--date', action="store", dest="initdate", help="Set initial date")
    parser.add_argument('--time', action="store", dest="inittime", help="Set initial time ")
    parser.add_argument('--modelid', action="store", dest="modelid", help="Set model id")

    result = parser.parse_args()

    #print "Initial date: {}\nInitial time: {}".format(result.initdate, result.inittime)
    
    main(result.initdate, result.inittime, result.modelid)
