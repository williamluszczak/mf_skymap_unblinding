#!/usr/bin/env python

import numpy as np
import sys
import os

rho = sys.argv[1]
Nflaresrc = sys.argv[2]

def decentry(inputseed, decband):
    decband = str(decband)
#    rho = str(0)
#    Nflaresrc = str(1)
    deltaT = str(10.0)
    jobentry = """JOB {0} bgmap_north.sub
VARS {0} inputseed=\"{1}\" dec=\"{2}\" rho=\"{3}\" Nflaresrc=\"{4}\" deltaT=\"{5}\"""".format((60*int(inputseed))+int(decband), inputseed, decband, rho, Nflaresrc, deltaT)
    return jobentry

for k in range(500,700):
    inputseed = str(k)
    decs = range(0,60)
    for dec in decs:
        jobentry = decentry(inputseed, dec)
        print(jobentry)
    
