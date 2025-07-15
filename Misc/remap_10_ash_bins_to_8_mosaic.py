import fractions
import numpy as np
from pandas import *
from utils import plot_fraction_histogram

# Example usage after you compute MOSAIC bin fractions:
# mos_fractions = [ ... ]  # your computed fractions for each MOSAIC bin
# plot_fraction_histogram(dlo_sectm, dhi_sectm, mos_fractions)
#grid with equal intervals on log-scale
dlo=0.0390625
dhi=10.0
nbin_o=8
nash=10

dlo_sectm=np.zeros(nbin_o)
dhi_sectm=np.zeros(nbin_o)
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
da_ash=array([1000.     ,  500.     ,  250.     ,  125.     ,  62.5    ,31.25   ,   15.625  ,    7.8125 ,    3.90625,    0.0391     ])
db_ash=array([2000.     , 1000.     ,  500.     ,  250.     ,  125.     ,62.5    ,   31.25   ,   15.625  ,    7.8125 ,   3.90625])


print ("\n")
print (str(nash)+" ASH BINS, diameter")
for n in range(0,nash):
    print (n+1,"{:10.4f}".format(da_ash[n]),"{:10.4f}".format(db_ash[n]))

print ("\n")

for m in range(0,nash):  # loop over ash size bins
    dlogoc = da_ash[m]  # low diameter limit
    dhigoc = db_ash[m]  # hi diameter limit

    for n in range(0,nbin_o):
        dustfrc_ash10bin_ln[m,n]=max(0.0,min(np.log(dhi_sectm[n]),np.log(dhigoc)) - max(np.log(dlogoc),np.log(dlo_sectm[n])))/(np.log(dhigoc)-np.log(dlogoc))

print ("\n")

print(DataFrame(dustfrc_ash10bin_ln, columns=[f"MOS{i+1}" for i in range(nbin_o)], index=[f"ASH{j+1}" for j in range(nash)]))


#Now, when the dustfrc_ash10bin_ln is ready, we can calculate the ash fractions

for i in range(0,nbin_o):
    print (f"\nMOS{i+1} = ",end='')
    for j in range(0,nash):
        if (dustfrc_ash10bin_ln[j,i]!=0.0):
            print (f"ASH{j+1} * {dustfrc_ash10bin_ln[j,i]} + ",end='')
print ("\n")

#these ash fractions are computed from given ash size distribution ASH1...ASH10
ash_mass_fractions = 0.01 * np.array([0.0, 0.0, 0.0, 0.0, 0.5, 7.3, 32.6, 42.2, 15.8, 1.7])
print (ash_mass_fractions)

#plot the histogram
fractions=ash_mass_fractions * 100
plot_fraction_histogram(da_ash, db_ash, fractions, title="Caluculated ASH mass Fractions")


print ("\n")
total_sum=0
remapped_mass_fractions=[]
for i in range(0,nbin_o):
    sum=0
    for j in range(0,nash):
        if (dustfrc_ash10bin_ln[j,i]!=0.0):
            sum+=ash_mass_fractions[j] * dustfrc_ash10bin_ln[j,i]

    print (f"MOS{i+1}={sum}")
    total_sum+=sum
    remapped_mass_fractions.append(sum*100)  # Convert to percentage

print(f"Total sum {total_sum} might not be equal to 1 as ASH1...ASH7 bins are out of the MOSAIC range.")

# Now, we can plot the remapped to MOSAIC ash fractions
plot_fraction_histogram(dlo_sectm, dhi_sectm, np.array(remapped_mass_fractions), title="Remappeed to MOSAIC grid ASH mass fractions")


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


10 ASH BINS, diameter
1  1000.0000  2000.0000
2   500.0000  1000.0000
3   250.0000   500.0000
4   125.0000   250.0000
5    62.5000   125.0000
6    31.2500    62.5000
7    15.6250    31.2500
8     7.8125    15.6250
9     3.9062     7.8125
10     0.0391     3.9062




           MOS1      MOS2      MOS3      MOS4      MOS5      MOS6      MOS7      MOS8
ASH1   0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000
ASH2   0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000
ASH3   0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000
ASH4   0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000
ASH5   0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000
ASH6   0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000
ASH7   0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000
ASH8   0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.356144
ASH9   0.000000  0.000000  0.000000  0.000000  0.000000  0.000000  0.356144  0.643856
ASH10  0.150338  0.150546  0.150546  0.150546  0.150546  0.150546  0.096930  0.000000

MOS1 = ASH10 * 0.15033796109924333 +
MOS2 = ASH10 * 0.15054636587660306 +
MOS3 = ASH10 * 0.15054636587660314 +
MOS4 = ASH10 * 0.15054636587660308 +
MOS5 = ASH10 * 0.1505463658766031 +
MOS6 = ASH10 * 0.1505463658766031 +
MOS7 = ASH9 * 0.35614381022527614 + ASH10 * 0.0969302095177412 +
MOS8 = ASH8 * 0.35614381022527614 + ASH9 * 0.6438561897747238 +

[0.    0.    0.    0.    0.005 0.073 0.326 0.422 0.158 0.017]


MOS1=0.002555745338687137
MOS2=0.002559288219902252
MOS3=0.0025592882199022534
MOS4=0.0025592882199022525
MOS5=0.002559288219902253
MOS6=0.002559288219902253
MOS7=0.057918535577395236
MOS8=0.2520219658994729
Total sum 0.32529268791506655 might not be equal to 1 as ASH1...ASH7 bins are out of the MOSAIC range.
'''