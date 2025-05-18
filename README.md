# PrepEmisSources
This preprocessor was developed to facilitate the preparation of volcanic emissions 
(chem_opt=402, emis_opt_vol=3) implemented in WRF-Chem starting from v.4.7.X.

## Dependancies:
conda install scipy,netCDF4,xarray,matplotlib,pandas

## How to use:
The path to the WRF-Chem's file with initial conditions (wrfinput_d01 in most cases) is 
required. Review the provided example*.py files and modify it to suit your specific 
requirements. After the script execution, the necessary adjustments to the namelist.input
file will be shown. For instance:

    &time_control
	    auxinput13_interval_m = 120.0
	    frames_per_auxinput13 = 6
	    auxinput13_inname     = 'wrfchemv_d01.1991-06-15_02:00:00'
    &chem
	    chem_opt               = 402
	    emiss_opt_vol          = 3

It means that prepared emission file 'wrfchemv_d01.1991-06-15_02:00:00' will be
read by WRF-Chem 6 times starting from the moment when the model time will pass 
'1991-06-15 02:00:00'. Interval between readings is 120 minutes.

This indicates that the prepared emission file ‘wrfchemv_d01.1991-06-15_02:00:00’ 
will be read by WRF-Chem 6 times, commencing from the moment when the model time 
reaches ‘1991-06-15 02:00:00’. The interval between each reading is 120 minutes.

## How to cite:
If you find this preprocessor useful, please do not forget to cite it as follows:
Ukhov et. al, Enhancing Volcanic Eruption Simulations with the WRF-Chem v4.7.X

## todo:
- fix bug if all zero profiles are used at the beginning, then profiles (QV for example) are not written to the netcdf file, But plot_how_much_was_written shows that they were written!!! (ex1.py).