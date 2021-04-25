#!/usr/bin/env python

import numpy as np
import glob
import sys
import healpy as hp

rho = 0
Nflare = 0

decband = float(sys.argv[1])

absmin = np.sin(np.radians(-85.))
absmax = np.sin(np.radians(-5.))
minsindec = absmin+((absmax-absmin)/20.)*decband
maxsindec = absmin+((absmax-absmin)/20.)*(decband+1)
print(minsindec, maxsindec)

def is_ind(pix1, pix2):
    dir1 = hp.pix2ang(256, pix1)
    dir2 = hp.pix2ang(256, pix2)

    angdist = hp.rotator.angdist(dir1, dir2)
    if angdist > np.radians(1.0):
        return True
    else:
        return False


bg_files = glob.glob('/data/user/wluszczak/multiflare_csky/gridmaps/*/combinedmap_south_*.npy')

sfts_dec = []
mfts_dec = []
for f in bg_files:
    if f != '/data/user/wluszczak/multiflare_csky/gridmaps/obs/combinedmap_north_obs.npy':
        print(f)
        bg_data = np.load(f, encoding='bytes', allow_pickle=True)
        bg_data = bg_data[np.sin(bg_data['dec'])>minsindec]
        bg_data = bg_data[np.sin(bg_data['dec'])<maxsindec]
        print(bg_data['dec'], len(bg_data))
        bg_pix = bg_data['ts']
        mfts_dec.extend(bg_pix)

        bg_flares = bg_data['flares'][bg_data['flares']!=None]
        maxflare = 0.
        for fcurve in bg_flares:
            if len(fcurve)>0:
                sfts_dec.append(fcurve['ts'][0])

np.save('/data/user/wluszczak/multiflare_csky/gridmaps/sindecbands/south_%s.npy'%(decband), sfts_dec)
np.save('/data/user/wluszczak/multiflare_csky/gridmaps/sindecbands/south_mf_%s.npy'%(decband), mfts_dec)
