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
import bisect

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import histlite as hl
import csky as cy
from csky import hyp

inputseed = int(sys.argv[1])
decband = int(sys.argv[2])
rho = str(sys.argv[3])
Nflaresrc = float(sys.argv[4])
deltaT = sys.argv[5]
SoBcut = 2000
#gamma = 2.28
gamma = 3.0
do_unblind = False
np.random.seed(seed=inputseed)

ana_dir = cy.utils.ensure_dir('/cvmfs/icecube.opensciencegrid.org/users/wluszczak/analyses/')
_local_root = os.getenv('CSKY_DATA_ANALYSES_DIR', '/cvmfs/icecube.opensciencegrid.org/users/wluszczak/analyses/')
_username = os.getenv('CSKY_REMOTE_USER', '')
repo = cy.selections.Repository(_local_root, '/cvmfs/icecube.opensciencegrid.org/users/wluszczak/analyses', username=_username)
ana = cy.get_analysis(repo, 'version-003-p02', cy.selections.PSDataSpecs.ps_10yr, dir=ana_dir)

sample_start = ana.mjd_min
sample_stop = ana.mjd_max
print("made ana object")

lowerdec = np.arcsin(np.sin(np.radians(-85.))+(0.909/30.)*(decband))
upperdec = np.arcsin(np.sin(np.radians(-85.))+(0.909/30.)*(decband+1))
print("decband", lowerdec, upperdec)

if deltaT == "None":
    deltaT = None
else:
    deltaT = float(deltaT)

print(rho)
if rho == '0':
    inj_flares = []
    srclist = cy.utils.Sources(ra=np.random.uniform(low=0., high=2.*np.pi, size=60), dec=np.linspace(0.,85.,60), name = range(0,60))
    for j in range(0,60):
        inj_flares.append([[56000.],j])
else:
    firefile = np.loadtxt('d%s_%s.out'%(rho, inputseed))
#    firefile = np.loadtxt('/data/user/wluszczak/FIRESONG-base/Results/d%s/d%s_%s.out'%(rho, rho, inputseed))

    firesong_decs = np.radians(firefile[:,0])
    firesong_ras = np.random.uniform(low=0, high=2.*np.pi, size=len(firesong_decs))
    firesong_srcfluxes = firefile[:,2]

    firesong_srcfluxes = firesong_srcfluxes[np.where((firesong_decs>lowerdec) & (firesong_decs<upperdec))]
    firesong_ras = firesong_ras[np.where((firesong_decs>lowerdec) & (firesong_decs<upperdec))]
    firesong_decs = firesong_decs[np.where((firesong_decs>lowerdec) & (firesong_decs<upperdec))]

    inj_flares = []
    visible_srcs = []
    csky_ind = 0
    events = 0
    src = cy.sources(firesong_ras[0], firesong_decs[0], deg=False)
    tr_src = cy.conf.get_trial_runner(src=src, ana=ana)
    srcfluxes = tr_src.to_ns(firesong_srcfluxes, gamma=2.28, E0=1e5, unit=1)
    srcfluxes = np.random.poisson(lam=srcfluxes)

    print("dec srcflux:", sum(srcfluxes))

    for srcind in range(0,len(firesong_srcfluxes)):
        srcflux = int(srcfluxes[srcind])
        howmanyflares = np.random.poisson(lam=Nflaresrc)
        if howmanyflares == 0:
            howmanyflares = 1
        possibletimes_src = np.arange(sample_start, sample_stop, 0.001)
        src_times = []

        flarelist = np.zeros(howmanyflares, dtype=int)
        for i in range(0,srcflux):
            which_flare = np.random.randint(low=0, high=howmanyflares)
            flarelist[which_flare]+=1
        for i in range(0, howmanyflares):
            flare_evts = flarelist[i]
            if flare_evts > 0:
                if len(possibletimes_src)==0:
                    print(flarelist, src_times)
                    print("no open sources, too many injected flares and not enough places to put them")
                    sys.exit()
                tcen = np.random.choice(possibletimes_src)
                possibletimes_src = possibletimes_src[abs(possibletimes_src-tcen)>deltaT*2.]
                times = np.random.uniform(low=tcen-deltaT, high=tcen+deltaT, size=flare_evts)
                src_times.extend(times)
        if len(src_times)>0:
            inj_flares.append([src_times, csky_ind])
            csky_ind+=1
            visible_srcs.append(srcind)
            events+=len(src_times)
            visible_flares = flarelist[flarelist>1]
            if len(visible_flares>0):
                print("visible flares", visible_flares)
    if len(visible_srcs)>0:
        visible_ras = firesong_ras[visible_srcs]
        visible_decs = firesong_decs[visible_srcs]
        srclist = cy.utils.Sources(ra=visible_ras, dec=visible_decs, name=range(0,len(visible_srcs)), deg=False)
    else:
        srclist = cy.utils.Sources(ra=[0.], dec=[0.], name = [0])
    
seedlist = []
seedlist.append(inputseed)

t1 = time.time()
msstr = cy.conf.get_sky_scan_trial_runner(ana=ana, multiflare=True, nside=256, threshold=SoBcut, max_dt=400., flux=hyp.PowerLawFlux(2.28), min_dec=lowerdec, max_dec=upperdec)
print("dec size", msstr.scan_dec.size)

inj_tr = cy.get_multiflare_trial_runner(ana=ana, src=srclist, muonflag=False, flux=hyp.PowerLawFlux(gamma), mp_cpus=1, threshold=SoBcut, filter_srcs=False) 

trial = inj_tr.get_one_trial(injflares=inj_flares, deltaT=deltaT, poisson=True, seed=inputseed, TRUTH=do_unblind, replace_evts=True, save_evts='data/injevts.npy')
print("trial", trial)

print("starting scan")
scan = msstr.get_one_scan_from_trial(trial, mp_cpus=1, TRUTH=do_unblind, seed=inputseed)
print(scan, scan.dtype.names)
tsarr = scan[1]
flarecurves = scan[7]
print(tsarr, flarecurves[flarecurves!=0.])
t2 = time.time()
print("time for a map", t2-t1)

np.savez('data/bgmap_south_%s_%s.npz'%(inputseed,decband), tsarr, flarecurves)
#np.savez('/data/user/wluszczak/multiflare_csky/testmap.npz', tsarr, flarecurves)
