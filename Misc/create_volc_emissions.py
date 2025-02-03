from netCDF4 import Dataset
import numpy as np
import os
import xarray as xr
import ukhov_jgr_supplementary as supplement
from scipy.interpolate import interp1d
from pandas import *
import datetime
import calendar

def  findClosetGridPoint(lats, lons, la,lo):
    nrow=len(lats)
    ncol=len(lons[0])
    #print(nrow, ncol)
    dist0=100.0
    ii=0
    jj=0
    for i in range(nrow):
        for j in range(ncol):
            dist=np.sqrt((lons[i,j]-lo)**2 +(lats[i,j]-la)**2)
            if (dist<dist0):
                dist0=dist
                jj=j
                ii=i
    return ii,jj,dist0


def add3dVar(wrf_file,var_name,caption,units):
    wrf_file.createVariable(var_name, 'f4', ('Time','bottom_top','south_north', 'west_east'))
    wrf_file.variables[var_name].FieldType=104
    wrf_file.variables[var_name].MemoryOrder="XYZ"
    wrf_file.variables[var_name].description=caption
    wrf_file.variables[var_name].units=units
    wrf_file.variables[var_name].stagger = "" ;
    wrf_file.variables[var_name].coordinates = "XLONG XLAT XTIME"

    #zero field
    wrf_file.variables[var_name][:] = 0.0
    print (f"Adding {var_name} {caption} {units} into {wrf_file}")


def add2dVar(wrf_file,var_name,caption,units):
    wrf_file.createVariable(var_name, 'f4', ('Time','south_north', 'west_east'))
    wrf_file.variables[var_name].FieldType=104
    wrf_file.variables[var_name].MemoryOrder="XY"
    wrf_file.variables[var_name].description=caption
    wrf_file.variables[var_name].units=units
    wrf_file.variables[var_name].stagger = "" ;
    wrf_file.variables[var_name].coordinates = "XLONG XLAT"

    #zero field
    wrf_file.variables[var_name][:] = 0.0
    print (f"Adding {var_name} {caption} {units} into {wrf_file}")


orgn_dir='/scratch/ukhova/SandBox/WRF/run_pinatubo_3month/'
orgn_wrf_input_file="wrfinput_d01"
dst_file="wrfchemv_d01"


#===========================================
#Read wrfinput
print (f'Open {orgn_dir}{orgn_wrf_input_file}')
wrfinput=Dataset(f'{orgn_dir}{orgn_wrf_input_file}','r')
xlon=wrfinput.variables['XLONG'][0,:]
xlat=wrfinput.variables['XLAT'][0,:]
MAPFAC_MX=wrfinput.variables['MAPFAC_MX'][0,:]
MAPFAC_MY=wrfinput.variables['MAPFAC_MY'][0,:]

dy = wrfinput.getncattr('DY')
dx = wrfinput.getncattr('DX')
surface = (dx/MAPFAC_MX)*(dy/MAPFAC_MY)       #surface in m2

Z = (wrfinput.variables['PH'][0,:] + wrfinput.variables['PHB'][0,:]) / 9.81
dz = np.diff(Z,axis=0)

Z = Z[:-1]
Z = Z + dz*0.5
Z = Z/1000.0

wrfinput.close()

#===========================================
if os.path.exists(f'{orgn_dir}{dst_file}'):
    os.system(f'rm {orgn_dir}{dst_file}')

ds = xr.open_dataset(f'{orgn_dir}{orgn_wrf_input_file}')
ds_var = ds[['PH','PHB','T','Times']]
ds_var.to_netcdf(f'{orgn_dir}{dst_file}')
#OR os.system(f'ncks -v ALB,Times {orgn_dir}{orgn_wrf_input_file} {orgn_dir}{dst_file}')
#===========================================

wrf_volc_file = Dataset(f'{orgn_dir}{dst_file}','r+')
add2dVar(wrf_volc_file,"ERUP_BEG","START TIME OF ERUPTION","?")
add2dVar(wrf_volc_file,"ERUP_END","END TIME OF ERUPTION","?")
add3dVar(wrf_volc_file,"E_VSO2","Volcanic Emissions, SO2","mol/m2/h")
add3dVar(wrf_volc_file,"E_VSULF","Volcanic Emissions, SULF","mol/m2/h")
add3dVar(wrf_volc_file,"E_QV","Volcanic Emissions, QV","kg/m2/s")

for i in range(1,11):
    add3dVar(wrf_volc_file,"E_VASH"+str(i),"Volcanic Emissions, bin"+str(i),"ug/m2/s")

#wrf_volc_file.close()

'''
We assume the same size distribution of the emitted
ash as that in Niemeier et al. (2009), Stenchikov et al. (2021) and allocate 0.1%, 1.5%, 9.5%, 45%, and 43.9% of
the mass to ash bins 1 to 5, respectively. The complex refractive index (RI) of the ash is set to 1.55 + i0.001
'''
gocart_fractions = 0.01 * np.array([0.1, 1.5, 9.5, 45,43.9])

ndust=5
nbin_o=10

#Size (um) Diametr
dlo_sectm=np.array([1e-5,3.90625,7.8125,15.625,31.25,62.5,125,250,500,1000])
dhi_sectm=np.array([3.90625,7.8125,15.625,31.25,62.5,125,250,500,1000,2000])

#Radii (um)
ra_gocart=np.array([0.1,1.0,1.8,3.0,6.0])
rb_gocart=np.array([1.0,1.8,3.0,6.0,10.0])
dustfrc_goc10bin_ln=np.zeros((ndust,nbin_o))

'''
3138   │ !1       1000    2000    -1 6.5  0   6.5     13  22  24  22  2.92    2.92    0  !
3139   │ !2       500     1000    0  12  4   12  20  5   25  5   3.55    3.55    0   !
3140   │ !3       250     500     1  18.75   10  18.75   27.5    4   20  4   11.82   11.82   0   !
3141   │ !4       125     250     2  36.25   50  36.25   22.5    5   12  5   8.24    8.24    9   !
3142   │ !5       62.5    125     3  20.5    34  20.5    7   24.5    9   24.5    7.9 7.9 22  !
3143   │ !6       31.25   62.5    4  3   2   3   4   12  4.25    12  13.02   13.02   23  !
3144   │ !7       15.625  31.25   5  1.5 0   1.5 3   11  3.25    11  16.28   16.28   21  !
3145   │ !8       7.8125  15.625  6  1   0   1   2   8   1.25    8   15.04   15.04   18  !
3146   │ !9       3.90625 7.8125  7  0.5 0   0.5 1   5   0.75    5   10.04   10.04   7   !
3147   │ !10      0   3.90625 8  0   0   0   0   3.5 0.5 3.5 11.19   11.19   0   !
'''

for m in range(0,ndust):  # loop over dust size bins
	dlogoc = ra_gocart[m]*2.0  # low diameter limit
	dhigoc = rb_gocart[m]*2.0  # hi diameter limit

	for n in range(0,4):
		dustfrc_goc10bin_ln[m,n]=max(0.0,min(np.log(dhi_sectm[n]),np.log(dhigoc)) - max(np.log(dlogoc),np.log(dlo_sectm[n])))/(np.log(dhigoc)-np.log(dlogoc))


#Flip dustfrc_goc10bin_ln because the smallest bin is Bin10, largset is Bin1
dustfrc_goc10bin_ln = np.fliplr(dustfrc_goc10bin_ln)
print (DataFrame(dustfrc_goc10bin_ln))

#one_day_in_seconds=86400                   #1 day = 86400 sec
volc_lats=[15.150110]
volc_lons=[120.346512]

start_year=[1991]
start_month=[6]
start_day=[15]
start_hour=[10]                                  #eruption start hour

#erup_start = datetime.datetime(1991, 6, 15, 1, 41)
#erup_dur_sec=[(14.0/24.0)*one_day_in_seconds]    #eruption duration in seconds

erup_dt=[600]    #eruption duration in minutes

volc_ash_emis_0=[60.0] #Mt
volc_so2_emis_0=[15.0] #Mt
volc_sulf_emis_0=[0.0] #Mt
volc_qv_emis_0=[150.0] #Mt

#TODO: remove
# Roll the array by 10 elements to the left
#supplement.inv_cumulative_emission_ash=np.roll(supplement.inv_cumulative_emission_ash, -10)
#supplement.inv_cumulative_emission_so2=np.roll(supplement.inv_cumulative_emission_so2, -10)

supplement.inv_cumulative_emission_so2 = np.zeros_like(supplement.inv_cumulative_emission_so2)
supplement.inv_cumulative_emission_ash = np.zeros_like(supplement.inv_cumulative_emission_ash)

supplement.inv_cumulative_emission_so2[7:17]=0.1
supplement.inv_cumulative_emission_ash[7:17]=0.1

print ('\n')
for i,lat in enumerate(volc_lats):
    print(f"{i+1}. Volcano coordinates: ",volc_lats[i],volc_lons[i])
    y,x,d=findClosetGridPoint(xlat, xlon, volc_lats[i],volc_lons[i])
    print (f'Found volcano at x={x} y={y}')
    
    f = interp1d(supplement.heights_on_levels/1000.0,supplement.inv_cumulative_emission_ash, kind='linear',fill_value="extrapolate")
    ash_interp = f(Z[:,y,x].data)   #Mt/m
    volc_ash_emis=np.sum(ash_interp * dz[:,y,x])
    print (volc_ash_emis)
    
    #Rescaling ash emissions
    ash_interp=ash_interp / (volc_ash_emis/volc_ash_emis_0[i])
    volc_ash_emis=np.sum(ash_interp * dz[:,y,x])
    print (volc_ash_emis)
    ash_interp *= dz[:,y,x]

    f = interp1d(supplement.heights_on_levels/1000.0,supplement.inv_cumulative_emission_so2, kind='linear',fill_value="extrapolate")
    so2_interp = f(Z[:,y,x].data)  #Mt/m
    volc_so2_emis=np.sum(so2_interp * dz[:,y,x])
    print (volc_so2_emis)
    
    #Rescaling SO2 emissions
    so2_interp=so2_interp / (volc_so2_emis/volc_so2_emis_0[i])
    volc_so2_emis=np.sum(so2_interp * dz[:,y,x])
    print (volc_so2_emis)
    so2_interp *= dz[:,y,x] #Mt per grid-cell
    
    #Sulf emissions. use so2 profile for now
    f = interp1d(supplement.heights_on_levels/1000.0,supplement.inv_cumulative_emission_so2, kind='linear',fill_value="extrapolate")
    sulf_interp = f(Z[:,y,x].data)  #Mt/m
    volc_sulf_emis=np.sum(sulf_interp * dz[:,y,x])
    print (volc_sulf_emis)
    
    #Rescaling SO2 emissions
    sulf_interp=sulf_interp / (volc_sulf_emis/volc_sulf_emis_0[i])
    volc_sulf_emis=np.sum(sulf_interp * dz[:,y,x])
    print (volc_sulf_emis)
    sulf_interp *= dz[:,y,x] #Mt per grid-cell
    
    #Ash emission in Mt/column. Need to make it in "ug/m2/s"
    for m in range(0,ndust):
        for n in range(0,nbin_o):
            wrf_volc_file.variables[f"E_VASH{n+1}"][0,:,y,x] += 1e18 * (dustfrc_goc10bin_ln[m,n] * gocart_fractions[m]) * ash_interp / (60 * erup_dt[i] * surface[y,x])
            #print(f"E_VASH{n+1}")
    
    #SO2 emission in Mt/column. Need to make it in "ug/m2/min"
    wrf_volc_file.variables['E_VSO2'][0,:,y,x] += 1e18 * so2_interp / (erup_dt[i] * surface[y,x])

    #SULF emission in Mt/column. Need to make it in "ug/m2/min"
    wrf_volc_file.variables['E_VSULF'][0,:,y,x] += 1e18 * sulf_interp / (erup_dt[i] * surface[y,x])

    #QV (water vapor) emission in Mt/column. Need to make it in "kg/m2/sec"
    #for now redistibute QV at the top of the domain. todo make suzuki!!!
    wrf_volc_file.variables['E_QV'][0,49,y,x] = 1e9 * (0.25 * volc_qv_emis_0[i]) / (60 * erup_dt[i] * surface[y,x])
    wrf_volc_file.variables['E_QV'][0,48,y,x] = 1e9 * (0.25 * volc_qv_emis_0[i]) / (60 * erup_dt[i] * surface[y,x])
    wrf_volc_file.variables['E_QV'][0,47,y,x] = 1e9 * (0.25 * volc_qv_emis_0[i]) / (60 * erup_dt[i] * surface[y,x])
    wrf_volc_file.variables['E_QV'][0,46,y,x] = 1e9 * (0.25 * volc_qv_emis_0[i]) / (60 * erup_dt[i] * surface[y,x])
    
    if calendar.isleap(start_year[i]):
        K = 1
    else:
        K = 2

    beg_jul = ((275 * start_month[i])/9) - K*((start_month[i]+9)/12) + start_day[i] - 30
    beg_jul = int(beg_jul)
    erup_beg = beg_jul * 1000. + start_hour[i]

    wrf_volc_file.variables['ERUP_BEG'][0,y,x] = erup_beg
    wrf_volc_file.variables['ERUP_END'][0,y,x] = erup_dt[i]
    
wrf_volc_file.close()
print ("DONE")