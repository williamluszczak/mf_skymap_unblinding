# Multiflare Skymap Unblinding

This respository contains the scripts for reproducing plots related to the IceCube 10 year multiflare skymap (https://wiki.icecube.wisc.edu/index.php/10_Year_Multiflare_Skymap). 

## Requirements
This repository should run with csky v1.1.1a (https://github.com/icecube/csky/releases/tag/v1.1.1a). 

## mapscripts
These scripts are used for calculating individual multiflare skymaps (either with data, scrambled data, or injected signal). Also included are submission scripts for running on the grid

## processingscripts
These scripts are for processing the raw files produced by running the scripts in the "mapscripts" directory on the grid. Includes files for combining grid outputs, calculating pre-trial p-values, and extracting sets of independent hotspots from a particular map. 

## plots
These scripts are for taking the processed data and making the plots seen on the wiki

## Making a skymap
The scripts included here are intended for use with the Grid (https://wiki.icecube.wisc.edu/index.php/Condor/Grid). Each skymap will be split over 60 (northern sky) or 30 (southern sky) jobs, split by declination band, each producing 1 output file. These files are then combined into a single .npy file containing information about the entire map. 

The first step in producing a skymap is to generate a dagman. This can be done with the makedag_bgmap_north.py and makedag_bgmap_south.py scripts:

makedag_bgmap_north.py $(rho) $(Nflare) $(output_dir)

$(rho) and $(Nflare) are the source density and number of flares per source, respectively. For a background map with no injected signal, set these to 0. $(output_dir) is the directory where the scripts will write the output files from the grid. For me this was in my /data/user/. An example call of this script looks like:

makedag_bgmap_north.py 0 0 /data/user/wluszczak/multiflare_csky/gridmaps/0/

Similarly, to generate maps of the southern sky:

makedag_bgmap_south.py 0 0 /data/user/wluszczak/multiflare_csky/gridmaps/0/

This will generate a dagman containing 60 (30 for the southern sky) entries corresponding to jobs for each declination band. These can then be submitted on sub-1.

## Processing skymap files
Once the skymap dagman has finished running (this may take a while), you should have 60 (30 for the southern sky) files in your output directory called "bgmap_north_0_0.npz" or similar. The first number in the file name refers to the seed, the second refers to the declination band. These files can be combined using the provided combine_v3.py (combine_v3_south.py for the southern sky):

combine_v3.py $(seednum) $(inputdir)

Where $(seednum) refers to the seed associated with the particular map generated (if you assembled original dagman using the included script, this will just be 0), and $(inputdir) is where your .npz files from the grid jobs are located.

After this script has run, you can safely delete the original .npz files. 

## Fitting Chi2 distributions for each dec band
Note: I've saved the per-decbin TS arrays to $(data_dir). You can extract these files yourself using the provided extract_sindecband.py script, provided you have an ensemble of bg maps already simulated. Currently, this script will read files from my /data/user/.



 
