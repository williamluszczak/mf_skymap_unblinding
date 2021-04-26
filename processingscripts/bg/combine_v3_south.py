#!/usr/bin/env python

import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import histlite as hl
import csky as cy
from csky import hyp
import healpy as hp
import os
import sys
import glob
import time

def getpixels():
    nside = 256
    npix = hp.nside2npix(nside)
    pixel_area = 4*np.pi/npix
    pixel_radius = np.sqrt(pixel_area/np.pi)
    print(pixel_area, pixel_radius)

    loc = np.empty(npix, dtype=[('ra', float), ('dec', float), ('ts', float), ('pix', int), ('flares', np.ndarray)])
    loc['pix'] = np.arange(npix)
    th, ph = hp.pix2ang(nside, loc['pix'])
    loc['dec'] = np.pi/2 - th
    loc['ra'] = ph
    loc['ts'] = np.zeros(np.shape(loc['ts']))

    return loc

pixarr = getpixels()

seednum = int(sys.argv[1])
inputdir = str(sys.argv[2])
#inputdir = '/data/user/wluszczak/multiflare_csky/gridmaps/%s/'%(seednum)

inj_evts = []
for decband in range(0,30):
    print(decband)
    data = np.load(inputdir+'/bgmap_south_%s_%s.npz'%(seednum, decband), allow_pickle=True, encoding='bytes')
    tsdata = data['arr_0']
    flaredata = data['arr_1']

    lowerdec = np.arcsin(np.sin(np.radians(-85.))+(0.909/30.)*(decband))
    upperdec = np.arcsin(np.sin(np.radians(-85.))+(0.909/30.)*(decband+1))
    whichpix = np.where((pixarr['dec']>=lowerdec) & (pixarr['dec']<upperdec))[0]

    tsdata = tsdata[whichpix]
    np.put(pixarr['ts'], whichpix, tsdata)

    flaredata = flaredata[whichpix]
    farrlist = []
    for flist in flaredata:
        if flist!=0.:
            farr = np.empty(len(flist), dtype=[('tstart', float), ('tstop', float), ('ts', float), ('ns', float), ('gamma', float)]) 
            farr['tstart'] = flist.mjd_start
            farr['tstop'] = flist.mjd_end
            farr['ts'] = flist.ts
            farr['ns'] = flist.ns
            farr['gamma'] = flist.gamma
        else:
            farr = np.array([])

        farrlist.append(farr)
    np.put(pixarr['flares'], whichpix, farrlist)

np.save(inputdir+'/combinedmap_south_%s.npy'%(seednum), pixarr)

fig, ax = plt.subplots (subplot_kw=dict (projection='aitoff'))
sp = cy.plotting.SkyPlotter(pc_kw=dict(cmap='jet'))
mesh, cb = sp.plot_map(ax, pixarr['ts'].astype(float), n_ticks=2)
kw = dict(color='.5', alpha=.5)
sp.plot_gp(ax, lw=.5, **kw)
sp.plot_gc(ax, **kw)
ax.grid(**kw)
cb.set_label(r'TS')
plt.savefig(inputdir+'/skymap_south_%s.png'%(seednum), dpi=500)

