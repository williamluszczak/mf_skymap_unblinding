#!/bin/bash

echo Starting script

ls /cvmfs/icecube.opensciencegrid.org/py2-v3/setup.sh
if [ $? -ne 0 ]; then
    echo "Problem setting up cvmfs"
    exit 1
else
    eval `/cvmfs/icecube.opensciencegrid.org/py2-v3/setup.sh`
fi

scratch_dir=$_CONDOR_SCRATCH_DIR
cd $scratch_dir
echo ${dir}
mkdir data

export PYTHONPATH="$PYTHONPATH:/cvmfs/icecube.opensciencegrid.org/users/wluszczak/packages/csky:/cvmfs/icecube.opensciencegrid.org/users/wluszczak/packages/"
echo $PATH
echo $PYTHONPATH

python check_env.py
if [ $? -ne 0 ]; then
    echo "Problem with environment"
    exit 1
else
    echo "check_env.py ran okay"
fi

if [ "$3" != 0 ]; then
    echo "Obtaining source data file"
    wget --user icecube --password skua https://convey.icecube.wisc.edu/data/user/wluszczak/FIRESONG-base/Results/d"$3"/d"$3"_"$1".out
else
    echo "Source density is 0, no need to get data file"
fi
 
echo Starting injmap.py
python injmap_north.py $1 $2 $3 $4 $5
globus-url-copy data/bgmap_north_"$1"_"$2".npz gsiftp://gridftp.icecube.wisc.edu/data/user/wluszczak/multiflare_csky/gridmaps/injmaps/d"$3"/"$4"flare/"$1"/
