# Multiflare Skymap Unblinding

This respository contains the scripts for reproducing plots related to the IceCube 10 year multiflare skymap (https://wiki.icecube.wisc.edu/index.php/10_Year_Multiflare_Skymap). 

## Requirements
This repository should run with csky v1.1.1a (https://github.com/icecube/csky/releases/tag/v1.1.1a). 

There are many pre-computed data files associated with the Reproducible_Plots ipython notebook that are currently stored in my /data/user/ at /data/user/wluszczak/mf_skymap_unblinding/data_dir/. This will be moved to /data/ana/, along with the full simulated skymap data (/data/user/wluszczak/multiflare_csky/gridmaps/) in the near future. 

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
Note: I've saved the per-decbin TS arrays to $(data_dir). You can extract these files yourself using the provided extract_sindecband.py script, provided you have an ensemble of bg maps already simulated. Currently, this script will read existing skymap files from my /data/user/.

Once the per-declination TS arrays are saved to file, you can preform chi2 fits using the code in the plots/Reproducible_Plots.ipynb ipython notebook, specifically in the cells labeled "Chi2 fits for declination bins". There are 4 sets of fits that need to be done, each corresponding to a single cell: nothern sky multiflare, northern sky single flare, southern sky multiflare, and southern sky single flare. Output plots showing the fits+residuals are written to the directory defined in the notebook.


## Converting TS maps to p-value maps
Once Chi2 fits have been verified, these fits can be used to convert the existing TS skymaps into p-value skymaps. This can be done with the pmap_north.py and pmap_south.py scripts:

pmap_north.py $(input_map) $(output_dir)

Where $(input_map) is the .npy file produced by combine_v3.py earlier, and $(output_dir) is where you want the output p-value map to be written.

## Extracting local hotspots
Once a p-value map is obtained, local hotspots (single or multi-flare) can be extracted with the extract_hotspots.py script:

extract_hotspots.py $(inputmap) $(outputfile) $(ptype)

Where $(inputmap) is the .npy file containing the full p-value map, $(outputfile) is where you want the output to be written, and $(ptype) is either "mf" or "sf", depending on whether you want to calculate the set of local multi-flare (mf) or single flare (sf) hotspots. Example usage would be:

extract_hotspots.py /data/user/wluszczak/multiflare_csky/gridmaps/0/pmap_north_0.npy /data/user/wluszczak/multiflare_csky/gridmaps/0/all_mf_hotspots_0.npy mf

Which will take the map calculated from seed 0 and extract the set of local multiflare hotspots, writing the output to the same directory. Note that this script can take a significant amount of time (~hours) to run. 

## Hypothesis testing for hotspots/populations
Once each map has an associated list of local hotspots, you can use this to conduct the hypothesis tests for the brightest multi/single flare spot, as well as population tests of the ensemble of local single/multi flare hotspots. The ipython notebook plots/Reproducible_Plots.ipynb shows background distributions assembled from the files located on my /data/user/ (to be moved to /data/ana/). 


## Single Source Tests
Tests involving only a single source can be run using the included single_src.py script in the single_src directory. Usage is as follows:

single_src.py $(inputseed) $(src_ra) $(src_dec) $(outfile) $(Nflare) $(flaresize) $(deltaT) $(gamma)

Where:

$(inputseed) is the seed you wish to run with
$(src_ra) is the right ascension of your source candidate, in radians
$(src_dec) is the declination of your source candidate, in radians
$(outfile) is where you want this script to write the output
$(Nflare) is the number of flares you wish to inject on this source. If you're running BG trials, set this to 0
$(flaresize) is the average number of events in each flare that you're injecting. If you're running BG trials, set this to 0
$(deltaT) is the flare half-duration, in days. e.g. deltaT=10 will inject flares with tstop-tstart=20 days
$(gamma) is the injected spectral index for the flares you will be injecting

The output of this script is a list of the flare fits in the form of a numpy recarr. You can obtain the fitted per-flare parameters with:

tstarts = flarecurve['tstart']
tstops = flarecurve['tstop']
ts = flarecurve['ts']
gamma = flarecurve['gamma']
ns = flarecurve['ns']

The multiflare ts for a particular trial is simply:

mf_ts = sum(flarecurve['ts'])

Where "flarecurve" is the flare curve recarr associated with a particular trial.

This script can be used to calculate a single source sensitivity, as well as inject/recover tests for ns and gamma. I have included appropriately sorted data files from running this script in the data_dir associated with this analysis (to be moved to /data/ana), which are then used in the Reproducible_Plots ipython notebook to make inj/recovery plots as well as a single-source sensitivity for NGC 1068(ra =-2.27e-4 rad, dec = 0.7096 rad).
