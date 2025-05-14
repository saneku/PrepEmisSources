## PrepEmisSources

This preprocessor was developed to facilitate the preparation of volcanic emissions used in WRF-Chem starting from v.4.7.X
If you find this preprocessor useful, please do not forget to cite it.

It is planned to extend to other emissions as well.

Ukhov et. al, Enhancing volcanic emissions...


# Dependancies:
conda install scipy,netCDF4,xarray,matplotlib,pandas




#todo:
- correct name for 3rd example
- convert to notebooks
- fix bug if all zero profiles are used in the beginning, then profiles (QV for example) are not written to the netcdf file, But plot_how_much_was_written shows that they were written!!! (ex1.py).
- add info on eruption time, duration, etc. to the netcdf file (ex2.py) see netcdf_handler.py
- add suzuki profile (ex2.py)
- add factors for profiles, so that they can be scaled up or down (ex3.py)
- remove extra stuff from netcdf_handler
- plot correctly profiles (ex3)