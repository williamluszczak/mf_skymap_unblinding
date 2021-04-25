#!/bin/bash

eval `/cvmfs/icecube.opensciencegrid.org/py2-v3/setup.sh`
python /data/user/wluszczak/multiflare_csky/gridmaps/injmaps/extract_hotspots_sf_north_sig.py $1 $2 $3
