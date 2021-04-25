#!/usr/bin/env python
import numpy as np
import matplotlib
matplotlib.use('agg')
import histlite as hl
import csky as cy
from scipy import stats
from scipy.stats import chi2
import sys
import healpy as hp
from scipy.optimize import curve_fit

def getpixels():
    nside = 256
    npix = hp.nside2npix(nside)
    pixel_area = 4*np.pi/npix
    pixel_radius = np.sqrt(pixel_area/np.pi)
    print(pixel_area, pixel_radius)

    loc = np.empty(npix, dtype=[('ra', float), ('dec', float), ('ts', float), ('ps_mf', float), ('ps_sf', float), ('pix', int), ('flares', np.ndarray)])
    loc['pix'] = np.arange(npix)
    th, ph = hp.pix2ang(nside, loc['pix'])
    loc['dec'] = np.pi/2 - th
    loc['ra'] = ph
    loc['ts'] = np.zeros(np.shape(loc['ts']))
    loc['ps_mf'] = np.zeros(np.shape(loc['ts']))
    loc['ps_sf'] = np.zeros(np.shape(loc['ts']))

    return loc


absmin = np.sin(np.radians(-5.))
absmax = np.sin(np.radians(85.))
sindecbands = []
chi2fits = {}
chi2fits_sf = {}

for decband in range(0,20):
    mindec = np.arcsin(absmin+(((absmax-absmin)/20.)*decband))
    maxdec = np.arcsin(absmin+(((absmax-absmin)/20.)*(decband+1)))
    print(np.degrees(mindec), np.degrees(maxdec))

    bg_ts = np.load('/data/user/wluszczak/multiflare_csky/gridmaps/sindecbands/20bins/%s.npy'%(float(decband)))
    print(len(bg_ts))
    if decband == 10:
        fithist, fitbins = np.histogram(bg_ts, bins = np.linspace(0,30,60), density=True)
    else:
        fithist, fitbins = np.histogram(bg_ts, bins = np.linspace(0,30,60), density=True)
    fitbins = fitbins[:-1]
    fitbin_centers = fitbins+(fitbins[1]-fitbins[0])*0.5

    fit_x = fitbin_centers[fithist>0.]
    fit_y = np.log10(fithist[fithist>0.])


    def f(x, ndof, loc, scale):
        return np.log10(stats.chi2.pdf(x, ndof, loc, scale))

    params, cov = curve_fit(f, fit_x, fit_y, p0=(9.64553646, -5.73856309,  1.74778147))
    chi2fits_sf[decband]=params


for decband in range(0,20):
    mindec = np.arcsin(absmin+(((absmax-absmin)/20.)*decband))
    maxdec = np.arcsin(absmin+(((absmax-absmin)/20.)*(decband+1)))
    print(np.degrees(mindec), np.degrees(maxdec))

    bg_ts = np.load('/data/user/wluszczak/multiflare_csky/gridmaps/sindecbands/20bins/mf_%s.npy'%(float(decband)))
    print(len(bg_ts))
    if decband == 10:
        fithist, fitbins = np.histogram(bg_ts, bins = np.linspace(0,60,120), density=True)
    else:
        fithist, fitbins = np.histogram(bg_ts, bins = np.linspace(0,60,120), density=True)
    fitbins = fitbins[:-1]
    fitbin_centers = fitbins+(fitbins[1]-fitbins[0])*0.5

    fit_x = fitbin_centers[fithist>0.]
    fit_y = np.log10(fithist[fithist>0.])


    def f(x, ndof, loc, scale):
        return np.log10(stats.chi2.pdf(x, ndof, loc, scale))

    params, cov = curve_fit(f, fit_x, fit_y, p0=(9.64553646, -5.73856309,  1.74778147))
    chi2fits[decband]=params

("finished chi2fits")
for i in range(0, 500):
    print(i)
    try:
        data = np.load('/data/user/wluszczak/multiflare_csky/gridmaps/%s/combinedmap_north_%s.npy'%(i,i), allow_pickle=True)

        pmap = getpixels()
        pmap['ra'] = data['ra']
        pmap['dec'] = data['dec']
        pmap['ts'] = data['ts']
        pmap['pix'] = data['pix']
        pmap['flares'] = data['flares']

        decmaxs = []
        decmaxps = []
        for decband in range(0,20):
            params = chi2fits[decband]
            params_sf = chi2fits_sf[decband]
            mindec = np.arcsin(absmin+(((absmax-absmin)/20.)*decband))
            maxdec = np.arcsin(absmin+(((absmax-absmin)/20.)*(decband+1)))

            whichpix = np.where((pmap['dec']>=mindec) & (pmap['dec']<maxdec))[0]
            decdata = data[whichpix] 
            
            decps_mf = 1.-chi2.cdf(decdata['ts'], params[0], params[1], params[2])
            np.put(pmap['ps_mf'], whichpix, decps_mf)

            whichpix = np.where((pmap['dec']>=mindec) & (pmap['dec']<maxdec) & (pmap['ts'] > 0.))[0]
            sfts = np.array([f['ts'][0] for f in decdata['flares'] if len(f)>0])
            decps_sf = 1.-chi2.cdf(sfts, params_sf[0], params_sf[1], params_sf[2])
            np.put(pmap['ps_sf'], whichpix, decps_sf)
    except IOError:
        pass
    print(pmap[np.argmax(pmap['ts'])])

    np.save('/data/user/wluszczak/multiflare_csky/gridmaps/%s/pmap_north_%s.npy'%(i, i), pmap)
