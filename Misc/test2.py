from netCDF4 import Dataset
import numpy as np
import os
import xarray as xr
from scipy.interpolate import interp1d
from pandas import *

#grid with equal intervals on log-scale
dlo=0.0390625
dhi=10.0
nbin_o=8
nash=10

dlo_sectm=np.zeros(nbin_o)
dhi_sectm=np.zeros(nbin_o)
xdia_um=np.zeros(nbin_o)
dustfrc_ash10bin_ln=np.zeros((nash,nbin_o))

xlo = np.log( dlo )
xhi = np.log( dhi )
dxbin = (xhi - xlo)/nbin_o

print (str(nbin_o)+" MOZAIC BINS, diameter")
dtemp=dlo
for n in range(0,nbin_o):
    dlo_sectm[n] = 2*np.exp( xlo + dxbin*(n-1) )
    dhi_sectm[n] = 2*np.exp( xlo + dxbin*n )

    print (n+1,"{:10.4f}".format(dlo_sectm[n]),"{:10.4f}".format(dhi_sectm[n]))

#Ash Size bins (um) Diametr, from higher to lower
ra_ash=array([1000.     ,  500.     ,  250.     ,  125.     ,  62.5    ,31.25   ,   15.625  ,    7.8125 ,    3.90625,    0.0391     ])
rb_ash=array([2000.     , 1000.     ,  500.     ,  250.     ,  125.     ,62.5    ,   31.25   ,   15.625  ,    7.8125 ,    3.90625])

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

for m in range(0,nash):  # loop over ash size bins
    dlogoc = ra_ash[m]  # low diameter limit
    dhigoc = rb_ash[m]  # hi diameter limit

    for n in range(0,nbin_o):
        dustfrc_ash10bin_ln[m,n]=max(0.0,min(np.log(dhi_sectm[n]),np.log(dhigoc)) - max(np.log(dlogoc),np.log(dlo_sectm[n])))/(np.log(dhigoc)-np.log(dlogoc))

print (DataFrame(dustfrc_ash10bin_ln))


'''
8 MOZAIC BINS, diameter
1     0.0391     0.0781
2     0.0781     0.1562
3     0.1562     0.3125
4     0.3125     0.6250
5     0.6250     1.2500
6     1.2500     2.5000
7     2.5000     5.0000
8     5.0000    10.0000

          0         1         2         3         4         5         6         7
0  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000
1  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000
2  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000
3  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000
4  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000
5  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000
6  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000
7  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.356144
8  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.356144  0.643856
9  0.150338  0.150546  0.150546  0.150546  0.150546  0.150546  0.096930  0.000000
'''