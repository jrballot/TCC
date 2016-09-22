#
# Makefile to compile the programs grbconv e grib2dp
#
# Those programs will convert a grib file to a RALPH2 dp file
# to use in BRAMS.
#
# To compile it, modify the following variables to meet your system
#
# FORTRAN 90 compiler
FC=gfortran
FCFLAGS=-static
#
# C Compiler
CC=gcc
CCFLAGS=-lm -static
# 
# Instructions to use it is located in the README file
#
# By P', PAD / CPTEC
# 
all: grbconv grib2dp

grbconv:
	$(CC) grbconv.c -o grbconv.x $(CCFLAGS)

grib2dp:
	$(FC) grib2dp.f90 -o grib2dp.x $(FCFLAGS)

clean:
	rm -f grbconv.x grib2dp.x
