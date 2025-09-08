[![DOI](https://zenodo.org/badge/16856541.svg)](https://zenodo.org/badge/latestdoi/16856541)

# PrepEmisSources
This preprocessor was developed to facilitate the preparation of volcanic emissions (chem_opt=402, emis_opt_vol=3) for the WRF-Chem v4.8 model.

## Dependencies:
scipy, netCDF4, xarray, matplotlib, pandas

## How to use:
The path to the WRF-Chem file with initial conditions ('wrfinput_d01', for example) is required. Please look over the provided 'example*.py' files and modify them to suit your requirements. 
After the script execution, the necessary adjustments in the namelist.input file will be shown. For instance:

    &time_control
	    auxinput13_interval_m = 10
	    frames_per_auxinput13 = 85
	    auxinput13_inname     = 'wrfchemv_d01.1991-06-15_01:40:00'
    &chem
	    chem_opt               = 402
	    emiss_opt_vol          = 3

These settings mean that the prepared emission file 'wrfchemv_d01.1991-06-15_01:40:00' will be read by WRF-Chem 85 times, starting from the moment when the model time passes '1991-06-15 01:40:00'.
During the run, the WRF-Chem model will read the data from the emission file at 10-minute intervals. Within each interval, the corresponding vertical distribution of emissions will be used.

## How to cite:
If you used this utility in your work, please do not forget to cite it as follows:
Ukhov et al., Enhancing Volcanic Eruption Simulations with the WRF-Chem v4.8.
