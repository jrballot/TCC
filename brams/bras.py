#!/usr/bin/env python
import re
import argparse
import os
from ftplib import FTP

# file format:  GAMRAMS+data+data[00,06,12,18].(icn|fct).TQ0126L028.(ctl|gmp|grb)
# necessario pegar o primeiro horario do dia seguinte

def validateEnv():
    pass


def downloadFiles(data):

    pattern = "GAMRAMS"+data+data[:-2]+"\d\dP.(icn|fct).TQ0126L028.(ctl|gmp|grb)"

    print pattern
    regex1 = re.compile(pattern)

    try:
        ftp = FTP("ftp1.cptec.inpe.br")
        ftp.login()
        ftp.cwd('/modelos/io/tempo/global/T126L28/'+data)
        print "List of files: \n"
        ftpFiles = ftp.nlst()
        for ftpFile in ftpFiles:
            if re.search(regex, ftpFile):
                print "Found match: {} downloading...".format(ftpFile)
                ftp.retrbinary('RETR %s' % ftpFile, open(os.path.join("./tmp",ftpFile), "wb").write )
    except Exception as e:
        print "Something goes wrong: {}".format(e)


def grib2dp():
    """
        grib2dp - Will try to covert the global input format from INPE to a DP format needed by BRAMS
    """

    pass

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
    downloadFiles(fullData)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="BRAS - BRAMS Automation Suit")
    parser.add_argument('--date', action="store", dest="initdate", help="Set initial date")
    parser.add_argument('--time', action="store", dest="inittime", help="Set initial time ")

    result = parser.parse_args()

    print "Initial date: {}\nInitial time: {}".format(result.initdate, result.inittime)

    main(result.initdate, result.inittime)
