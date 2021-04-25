#!/usr/bin/env python
import numpy as np
import matplotlib
matplotlib.use('agg')
import histlite as hl
import csky as cy
from scipy import stats
from scipy.stats import chi2
import sys
from scipy.optimize import curve_fit

counter = int(sys.argv[1])
chunksize = 50

mindecs = []
minps = []

startind = chunksize*counter
endind = chunksize*(counter+1)

absmin = np.sin(np.radians(-5.))
absmax = np.sin(np.radians(85.))
sindecbands = []
chi2fits = {}

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

print("finished chi2fits")
for i in range(startind, endind):
    print(i)
    try:
        data = np.load('/data/user/wluszczak/multiflare_csky/gridmaps/%s/combinedmap_north_%s.npy'%(i,i), allow_pickle=True)
        decmaxs = []
        decmaxps = []
        for decband in range(0,20):
            params = chi2fits[decband]
            mindec = np.arcsin(absmin+(((absmax-absmin)/20.)*decband))
            maxdec = np.arcsin(absmin+(((absmax-absmin)/20.)*(decband+1)))

            decdata = data[(data['dec']>=mindec) & (data['dec']<maxdec)]

            sorteddata = np.sort(decdata, order='ts')[::-1]
            maxpix = sorteddata[0]
            maxpixts = maxpix['ts']
            maxpixdec = maxpix['dec']
            maxpixp = 1.-chi2.cdf(maxpixts, params[0], params[1], params[2])
            decmaxs.append([maxpixp, maxpixdec])
        decmaxs_sorted = sorted(decmaxs)
        mapmax = decmaxs_sorted[0]
        print(mapmax[1])
        mindecs.append(mapmax[1])
        minps.append(mapmax)
    except IOError:
        pass

np.save('/data/user/wluszczak/multiflare_csky/gridmaps/photspots/minp_decs_sindecbins_%s.npy'%(counter), mindecs)
