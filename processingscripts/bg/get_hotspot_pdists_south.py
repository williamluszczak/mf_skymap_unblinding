#!/usr/bin/env python

import numpy as np

hotps_mf = []
hotps_sf = []
for i in range(0,500):
    try:
        processed_data = np.load('/data/user/wluszczak/multiflare_csky/gridmaps/%s/south_hotspots_%s.npy'%(i, i), allow_pickle=True)
        hotps_mf.append(min(processed_data['ps_mf']))
        hotps_sf.append(min(processed_data['ps_sf']))
    except IOError:
        pass

print(hotps_mf)
print(hotps_sf)

np.save('/data/user/wluszczak/multiflare_csky/gridmaps/hotps_mf_south.npy', hotps_mf)
np.save('/data/user/wluszczak/multiflare_csky/gridmaps/hotps_sf_south.npy', hotps_sf)
