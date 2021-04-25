#!/usr/bin/env python

import numpy as np
import sys
import os

rho = sys.argv[1]
Nflaresrc = sys.argv[2]

def decentry(inputseed):
    deltaT = str(10.0)
    jobentry = """JOB {0} extract_hotspots_mf_north_sig.sub
VARS {0} rho=\"{1}\" Nflaresrc=\"{2}\" seednum=\"{0}\"""".format(inputseed, rho, Nflaresrc)
    return jobentry

for k in range(0,50):
    inputseed = str(k)
    jobentry = decentry(inputseed)
    print(jobentry)
    
