# Multiflare Skymap Unblinding

This respository contains the scripts for reproducing plots related to the IceCube 10 year multiflare skymap (https://wiki.icecube.wisc.edu/index.php/10_Year_Multiflare_Skymap). 

## mapscripts
These scripts are used for calculating individual multiflare skymaps (either with data, scrambled data, or injected signal). Also included are submission scripts for running on the grid

## processingscripts
These scripts are for processing the raw files produced by running the scripts in the "mapscripts" directory on the grid. Includes files for combining grid outputs, calculating pre-trial p-values, and extracting sets of independent hotspots from a particular map. 

## plots
These scripts are for taking the processed data and making the plots seen on the wiki
