import numpy as np
from pandas import DataFrame

# remaping fractors: 
# from 5 bin GOCART to 10 ash bins

#Diametr (um)
da_gocart=np.array([ 0.2, 2. , 3.6, 6. , 12. ])
db_gocart=np.array([ 2. , 3.6, 6. , 12., 20. ])
ndust=5

print ("\n")
print (str(ndust)+" GOCART BINS, diameter")
for n in range(0,ndust):
    print (n+1,"{:10.4f}".format(da_gocart[n]),"{:10.4f}".format(db_gocart[n]))

print ("\n")




nbin_o=10

#Size (um) Diametr of 10 ash bins
dlo_sectm=np.array([1e-5,3.90625,7.8125,15.625,31.25,62.5,125,250,500,1000])
dhi_sectm=np.array([3.90625,7.8125,15.625,31.25,62.5,125,250,500,1000,2000])

print ("\n")
print (str(nbin_o)+" ASH BINS, diameter")
for n in range(0,nbin_o):
    print (n+1,"{:10.4f}".format(dlo_sectm[n]),"{:10.4f}".format(dhi_sectm[n]))

print ("\n")



dustfrc_goc10bin_ln=np.zeros((ndust,nbin_o))
for m in range(0,ndust):  # loop over dust size bins
	dlogoc = da_gocart[m]  # low diameter limit
	dhigoc = db_gocart[m]  # hi diameter limit

	for n in range(0,4):
		dustfrc_goc10bin_ln[m,n]=max(0.0,min(np.log(dhi_sectm[n]),np.log(dhigoc)) - max(np.log(dlogoc),np.log(dlo_sectm[n])))/(np.log(dhigoc)-np.log(dlogoc))

#Flip dustfrc_goc10bin_ln because the smallest bin is Bin10, largset is Bin1
dustfrc_goc10bin_ln = np.fliplr(dustfrc_goc10bin_ln)
#print (DataFrame(dustfrc_goc10bin_ln))
print(DataFrame(dustfrc_goc10bin_ln, columns=[f"ASH{i+1}" for i in range(nbin_o)], index=[f"GOC{j+1}" for j in range(ndust)]))

#Now remap the GOCART fractions to ASH fractions
gocart_fractions = 0.01 * np.array([0.1, 1.5, 9.5, 45, 43.9])
print (gocart_fractions)

for i in range(6,10)[::-1]:
    print (f"\nASH{i+1}=",end='')
    for j in range(0,5):
        if (dustfrc_goc10bin_ln[j,i]!=0.0):
            print (f"GOC{j+1} * {dustfrc_goc10bin_ln[j,i]} + ",end='')

print ("\n")
total_sum=0
for i in range(6,10)[::-1]:
    sum=0
    for j in range(0,5):
        if (dustfrc_goc10bin_ln[j,i]!=0.0):
            sum+=gocart_fractions[j] * dustfrc_goc10bin_ln[j,i]

    print (f"ASH{i+1}={sum}")
    total_sum+=sum

print(f"Total sum {total_sum}. And it SHOULD be equal to 1 as ASH range covers GOCART range.")

#        ash1 ash2  3    4   ash5  6      ash7     ash8       ash9     ash10
# dust1  0.0  0.0  0.0  0.0  0.0  0.0  0.000000  0.000000  0.000000  1.000000
# dust2  0.0  0.0  0.0  0.0  0.0  0.0  0.000000  0.000000  0.000000  1.000000
# dust3  0.0  0.0  0.0  0.0  0.0  0.0  0.000000  0.000000  0.840172  0.159828
# dust4  0.0  0.0  0.0  0.0  0.0  0.0  0.000000  0.619178  0.380822  0.000000
# dust5  0.0  0.0  0.0  0.0  0.0  0.0  0.483257  0.516743  0.000000  0.000000

'''
Ash10=0.03118361373822074
Ash9=0.2511861890351982
Ash8=0.5054803574965663
Ash7=0.21214983973001478
Ash1, Ash2, Ash3, Ash4, ... , Ash9, Ash10
[0,0,0,0,0,0,0.2109,0.5060,0.2519,0.03120]
'''
