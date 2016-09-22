#!/usr/bin/env python
import re
import argparse
import os
import shutil
import subprocess
from ftplib import FTP

# file format:  GAMRAMS+data+data[00,06,12,18].(icn|fct).TQ0126L028.(ctl|gmp|grb)
# necessario pegar o primeiro horario do dia seguinte
_pathTMP = os.path.join(os.path.abspath("."),"tmp/regional")
_pathREGIONAL = os.path.join(os.path.abspath("."),"tmp/regional")
_grib2dp = os.path.join(os.path.abspath("."),"grib2dp")


def preRun():

    """
        Validade prerequisits to run the model
    """


    if not os.path.exists(_pathTMP):
        os.makedirs(_pathTMP)

    if not os.path.exists(_pathREGIONAL):
        os.makedirs(_pathREGIONAL)
    else:
        #clean content
        pass






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
                print "Found match: {} downloading...".format(ftpFile)
                ftp.retrbinary('RETR %s' % ftpFile, open(os.path.join(_pathREGIONAL,ftpFile), "wb").write )
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
        subprocess.call([_pathREGIONAL+"/grib2dp.x"])
    except Exception as e:
        print "Something goes wrong: {}".format(e)

def copyDP():
    "copyDP - Copy DP files to your proper destination inside BRAMS's hierarchy directories"
    pass

def runModel(runtype):
    """
        runModel - Run BRAMS with a especified RUNTYPE passed by runtype variable.
        Runtype can be one of those:
            INITIAL
            MAKESFC
            MAKEVFILE
    """
    pass

def getOutputInPNG():
    """
        getOutputInPNG - convert output from BRAMS in a PNG image
    """
    pass

def main(date,time):
    """
        main - it's control the main flow
    """

    if time[:1] < 12:
        time = '00'
    else:
        time = '12'

    fullData = date+time
    nextday = date[:-2] + str(int(date[-2:])+1)

    preRun()
    downloadFiles(fullData,nextday)
    grib2dp()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BRAS - BRAMS Automation Suit")
    parser.add_argument('--date', action="store", dest="initdate", help="Set initial date")
    parser.add_argument('--time', action="store", dest="inittime", help="Set initial time ")

    result = parser.parse_args()

    print "Initial date: {}\nInitial time: {}".format(result.initdate, result.inittime)

    main(result.initdate, result.inittime)
