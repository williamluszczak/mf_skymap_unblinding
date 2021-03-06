#!/usr/bin/env python

import numpy as np
import glob
import sys
import healpy as hp
import time

rho = 0
Nflare = 0
#seednum = int(sys.argv[1])
inputmap = str(sys.argv[1])
outputfile = str(sys.argv[2])
ptype = str(sys.argv[3]) #either 'mf' or 'sf'

def is_ind(pix1, pix2):
    dir1 = hp.pix2ang(256, pix1)
    dir2 = hp.pix2ang(256, pix2)

    angdist = hp.rotator.angdist(dir1, dir2)
    if angdist > np.radians(1.0):
        return True
    else:
        return False


bg_data = np.load(inputmap, encoding='bytes', allow_pickle=True)

bg_data = bg_data[bg_data['ts']>0.]
if ptype == 'mf':
    sorted_data = np.sort(bg_data, order='ps_mf')
if ptype == 'sf':
    sorted_data = np.sort(bg_data, order='ps_sf')
remaining_data = np.copy(sorted_data)
hotspots = []
excluded_pix = []
k = 0
for hotspot in sorted_data:
    k+=1
    if hotspot['pix'] in excluded_pix:
        pass
    elif len(remaining_data)>1:
        t1 = time.time()
        hotspots.append(hotspot)
        hotdir = hp.pix2ang(256, hotspot['pix'])
        testdirs = hp.pix2ang(256, remaining_data['pix'])
        distances = hp.rotator.angdist(hotdir, testdirs)
        closeby = remaining_data[distances<np.radians(1.)]
        pix_to_delete = closeby['pix']
        inds_to_delete = np.in1d(remaining_data['pix'], pix_to_delete).nonzero()[0]
        excluded_pix.extend(pix_to_delete)
        remaining_data = np.delete(remaining_data, inds_to_delete)
        t2 = time.time()
        print("hotspot time", t2-t1, k, len(hotspots))       
     
#np.save('/data/user/wluszczak/multiflare_csky/gridmaps/%s/north_hotspots_mf_%s.npy'%(j, j), hotspots)
np.save(outputfile, hotspots)

