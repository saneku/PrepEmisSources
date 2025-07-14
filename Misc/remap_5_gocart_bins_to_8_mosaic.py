import numpy as np
from pandas import DataFrame

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
print (gocart_fractions)

print ("\n")
total_sum=0
for i in range(0,nbin_o):
    sum=0
    for j in range(0,ndust):
        if (dustfrc_goc8bin_ln[j,i]!=0.0):
            sum+=gocart_fractions[j] * dustfrc_goc8bin_ln[j,i]

    print (f"MOS{i+1}={sum}")
    total_sum+=sum

print(f"Total sum {total_sum} might not be equal to 1 as 5th GOCART bin is out of the MOSAIC range.")