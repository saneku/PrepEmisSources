import numpy as np
from pandas import DataFrame
from utils import plot_fraction_histogram

# remaping fractors: 
# from 5 bin GOCART to 8 MOSAIC bins

#Diametr (um)
da_gocart=np.array([ 0.2, 2. , 3.6, 6. , 12. ])
db_gocart=np.array([ 2. , 3.6, 6. , 12., 20. ])
ndust=5

print ("\n")
print (str(ndust)+" GOCART BINS, diameter")
for n in range(0,ndust):
    print (n+1,"{:10.4f}".format(da_gocart[n]),"{:10.4f}".format(db_gocart[n]))

print ("\n")

#MOSAIC grid with equal intervals on log-scale
dlo=0.0390625
dhi=10.0
nbin_o=8

dlo_sectm=np.zeros(nbin_o)
dhi_sectm=np.zeros(nbin_o)

xlo = np.log( dlo )
xhi = np.log( dhi )
dxbin = (xhi - xlo)/nbin_o

print (str(nbin_o)+" MOZAIC BINS, diameter")
dtemp=dlo
for n in range(0,nbin_o):
    dlo_sectm[n] = 2*np.exp( xlo + dxbin*(n-1) )
    dhi_sectm[n] = 2*np.exp( xlo + dxbin*n )

    print (n+1,"{:10.4f}".format(dlo_sectm[n]),"{:10.4f}".format(dhi_sectm[n]))


print ("\n")
dustfrc_goc8bin_ln=np.zeros((ndust,nbin_o))

for m in range(0,ndust):  # loop over dust size bins
	dlogoc = da_gocart[m]  # low diameter limit
	dhigoc = db_gocart[m]  # hi diameter limit

	for n in range(0,nbin_o):
		dustfrc_goc8bin_ln[m,n]=max(0.0,min(np.log(dhi_sectm[n]),np.log(dhigoc)) - max(np.log(dlogoc),np.log(dlo_sectm[n])))/(np.log(dhigoc)-np.log(dlogoc))

print(DataFrame(dustfrc_goc8bin_ln, columns=[f"MOS{i+1}" for i in range(nbin_o)], index=[f"GOC{j+1}" for j in range(ndust)]))
print ("\n")

#Now, when the dustfrc_goc8bin_ln is ready, we can calculate the ash fractions
for i in range(0,nbin_o):
    print (f"\nMOS{i+1} = ",end='')
    for j in range(0,ndust):
        if (dustfrc_goc8bin_ln[j,i]!=0.0):
            print (f"GOC{j+1} * {dustfrc_goc8bin_ln[j,i]} + ",end='')


gocart_fractions = 0.01 * np.array([0.1, 1.5, 9.5, 45, 43.9])
print ("\n")
print (gocart_fractions)

#plot the histogram
fractions=gocart_fractions*100
plot_fraction_histogram(da_gocart, db_gocart, fractions, title="Caluculated GOCART mass Fractions")


print ("\n")
total_sum=0
remapped_mass_fractions=[]
for i in range(0,nbin_o):
    sum=0
    for j in range(0,ndust):
        if (dustfrc_goc8bin_ln[j,i]!=0.0):
            sum+=gocart_fractions[j] * dustfrc_goc8bin_ln[j,i]

    print (f"MOS{i+1}={sum}")
    total_sum+=sum
    remapped_mass_fractions.append(sum*100)  # Convert to percentage

print(f"Total sum {total_sum} might not be equal to 1 as 5th GOCART bin is out of the MOSAIC range.")

# Now, we can plot the remapped to MOSAIC ash fractions
plot_fraction_histogram(dlo_sectm, dhi_sectm, np.array(remapped_mass_fractions), title="Remappeed to MOSAIC grid GOCART mass fractions")


'''
5 GOCART BINS, diameter
1     0.2000     2.0000
2     2.0000     3.6000
3     3.6000     6.0000
4     6.0000    12.0000
5    12.0000    20.0000


8 MOZAIC BINS, diameter
1     0.0391     0.0781
2     0.0781     0.1562
3     0.1562     0.3125
4     0.3125     0.6250
5     0.6250     1.2500
6     1.2500     2.5000
7     2.5000     5.0000
8     5.0000    10.0000


      MOS1  MOS2     MOS3     MOS4     MOS5      MOS6      MOS7      MOS8
GOC1   0.0   0.0  0.19382  0.30103  0.30103  0.204120  0.000000  0.000000
GOC2   0.0   0.0  0.00000  0.00000  0.00000  0.379634  0.620366  0.000000
GOC3   0.0   0.0  0.00000  0.00000  0.00000  0.000000  0.643085  0.356915
GOC4   0.0   0.0  0.00000  0.00000  0.00000  0.000000  0.000000  0.736966
GOC5   0.0   0.0  0.00000  0.00000  0.00000  0.000000  0.000000  0.000000



MOS1 =
MOS2 =
MOS3 = GOC1 * 0.1938200260161129 +
MOS4 = GOC1 * 0.3010299956639812 +
MOS5 = GOC1 * 0.30102999566398125 +
MOS6 = GOC1 * 0.20411998265592465 + GOC2 * 0.37963357224405403 +
MOS7 = GOC2 * 0.620366427755946 + GOC3 * 0.6430845511432771 +
MOS8 = GOC3 * 0.35691544885672283 + GOC4 * 0.7369655941662071 + [0.001 0.015 0.095 0.45  0.439]



MOS1=0
MOS2=0
MOS3=0.00019382002601611289
MOS4=0.0003010299956639812
MOS5=0.00030102999566398124
MOS6=0.005898623566316734
MOS7=0.07039852877495051
MOS8=0.3655414850161819
Total sum 0.4426345173747932 might not be equal to 1 as 5th GOCART bin is out of the MOSAIC range.
'''