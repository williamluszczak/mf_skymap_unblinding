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
print(len(pixarr[pixarr['dec']<np.radians(-5.)]))
sys.exit()

#rho = str(sys.argv[1])
#Nflaresrc = sys.argv[2]
seednum = int(sys.argv[1])

inj_evts = []
for decband in range(0,30):
    print(decband)
    data = np.load('/data/user/wluszczak/multiflare_csky/gridmaps/%s/bgmap_south_%s_%s.npz'%(seednum, seednum, decband), allow_pickle=True, encoding='bytes')
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

#    inj_data = np.load('/data/user/wluszczak/multiflare_csky/gridmaps/injmaps/d%s/%sflare/%s/inj_evts_south_%s_%s.npy'%(rho, Nflaresrc, seednum, seednum, decband), allow_pickle=True, encoding='bytes')
#    if len(inj_data)>0:
#        inj_evts.append(np.concatenate(inj_data))

#inj_evts = np.concatenate(inj_evts)

np.save('/data/user/wluszczak/multiflare_csky/gridmaps/%s/combinedmap_south_%s.npy'%(seednum, seednum), pixarr)
#np.save('/data/user/wluszczak/multiflare_csky/gridmaps/injmaps/d%s/%sflare/%s/all_inj_evts_south_%s.npy'%(rho, Nflaresrc, seednum, seednum), inj_evts)

fig, ax = plt.subplots (subplot_kw=dict (projection='aitoff'))
sp = cy.plotting.SkyPlotter(pc_kw=dict(cmap='jet'))
#mesh, cb = sp.plot_map(ax, pixarr['ts'].astype(float), n_ticks=2, pc_kw={'vmin':0., 'vmax':100.})
mesh, cb = sp.plot_map(ax, pixarr['ts'].astype(float), n_ticks=2)
kw = dict(color='.5', alpha=.5)
sp.plot_gp(ax, lw=.5, **kw)
sp.plot_gc(ax, **kw)
ax.grid(**kw)
cb.set_label(r'TS')
plt.savefig('/data/user/wluszczak/multiflare_csky/gridmaps/%s/skymap_south_%s.png'%(seednum, seednum), dpi=500)

