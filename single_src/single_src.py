#!/usr/bin/env python

import numpy as np
import healpy as hp
import os
import sys
import itertools
import time
import glob
from operator import itemgetter
from math import floor

import scipy.optimize


import matplotlib
matplotlib.use('agg')
import histlite as hl
import csky as cy
from csky import hyp

inputseed = int(sys.argv[1])
src_ra = float(sys.argv[2])
src_dec = float(sys.argv[3])
outfile = str(sys.argv[4])
Nflare = float(sys.argv[5])
flaresize = float(sys.argv[6])
deltaT = float(sys.argv[7])
gamma = float(sys.argv[8])
SoBcut = 1000.
alpha = 999999.
do_unblind = False
np.random.seed(seed=inputseed)

if deltaT == "None":
    deltaT = None
else:
    deltaT = float(deltaT)

ana_dir = cy.utils.ensure_dir('/cvmfs/icecube.opensciencegrid.org/users/wluszczak/analyses/')
_local_root = os.getenv('CSKY_DATA_ANALYSES_DIR', '/cvmfs/icecube.opensciencegrid.org/users/wluszczak/analyses/')
_username = os.getenv('CSKY_REMOTE_USER', '')
repo = cy.selections.Repository(_local_root, '/cvmfs/icecube.opensciencegrid.org/users/wluszczak/analyses', username=_username)

ana = cy.get_analysis(repo, 'version-003-p02', cy.selections.PSDataSpecs.ps_10yr[0], dir=ana_dir)

full_srclist = cy.utils.Sources(ra=src_ra, dec=src_dec, name=0)
mtr = cy.get_multiflare_trial_runner(ana=ana, src=full_srclist, muonflag=False, flux=hyp.PowerLawFlux(gamma), mp_cpus=1, threshold=SoBcut, filter_srcs=True, max_dt=300.)


cfits = []
seedlist = []
plist = []
for k in range(0,2):
    print(k)
    np.random.seed(seed=inputseed+k)
    seedlist.append(inputseed+k)

    t1 = time.time()
    inj_srclist = full_srclist

    inj_tr = cy.get_multiflare_trial_runner(ana=ana, src=inj_srclist, muonflag=False, flux=hyp.PowerLawFlux(gamma), mp_cpus=1, threshold=SoBcut, filter_srcs=False, max_dt=300.)
    trial=inj_tr.get_one_trial(Am=Nflare, Io=flaresize, alpha=alpha, deltaT=deltaT, poisson=True, seed=inputseed+k, TRUTH=do_unblind)

    print("starting fit")
    cfit = mtr.get_one_fit_from_trial(trial, mp_cpus=1, TRUTH=True, flat=False, decorrelate=True)
    cfit_sorted = sorted(cfit.items(), key=lambda e: e[1][0], reverse=True)
    sorted_ts = [fit[1][0] for fit in cfit_sorted]
    print(sorted_ts)
    t2 = time.time()
    print("time for TS", t2-t1)

    cfits.append(cfit)
    print(cfit.values()[0][-1])

print("start conversion")
farrs = []
for r in cfits:
    flist = r.values()[0][-1]
    farr = np.empty(len(flist), dtype=[('tstart', float), ('tstop', float), ('ts', float), ('ns', float), ('gamma', float)])
    farr['tstart'] = flist.mjd_start
    farr['tstop'] = flist.mjd_end
    farr['ts'] = flist.ts
    farr['ns'] = flist.ns
    farr['gamma'] = flist.gamma
    farrs.append(farr)

np.save(outfile, farrs)
#np.savez('filtered_windows.npz', cfits)
