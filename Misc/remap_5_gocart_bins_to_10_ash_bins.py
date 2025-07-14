import numpy as np
from pandas import DataFrame

# remaping fractors: 
# from 5 bin GOCART to 10 ash bins

#Diametr (um)
da_gocart=np.array([ 0.2, 2. , 3.6, 6. , 12. ])
db_gocart=np.array([ 2. , 3.6, 6. , 12., 20. ])

gocart_fractions = 0.01 * np.array([0.1, 1.5, 9.5, 45,43.9])
print (gocart_fractions)

ndust=5
nbin_o=10

#Size (um) Diametr of 10 ash bins
dlo_sectm=np.array([1e-5,3.90625,7.8125,15.625,31.25,62.5,125,250,500,1000])
dhi_sectm=np.array([3.90625,7.8125,15.625,31.25,62.5,125,250,500,1000,2000])


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
	dlogoc = da_gocart[m]  # low diameter limit
	dhigoc = db_gocart[m]  # hi diameter limit

	for n in range(0,4):
		dustfrc_goc10bin_ln[m,n]=max(0.0,min(np.log(dhi_sectm[n]),np.log(dhigoc)) - max(np.log(dlogoc),np.log(dlo_sectm[n])))/(np.log(dhigoc)-np.log(dlogoc))

#Flip dustfrc_goc10bin_ln because the smallest bin is Bin10, largset is Bin1
dustfrc_goc10bin_ln = np.fliplr(dustfrc_goc10bin_ln)
print (DataFrame(dustfrc_goc10bin_ln))


for i in range(6,10)[::-1]:
    print (f"\nAsh{i+1}=",end='')
    for j in range(0,5):
        if (dustfrc_goc10bin_ln[j,i]!=0.0):
            print (f"dust{j+1} * {dustfrc_goc10bin_ln[j,i]} + ",end='')

print ("\n")
total_sum=0
for i in range(6,10)[::-1]:
    sum=0
    for j in range(0,5):
        if (dustfrc_goc10bin_ln[j,i]!=0.0):
            sum+=gocart_fractions[j] * dustfrc_goc10bin_ln[j,i]

    print (f"Ash{i+1}={sum}")
    total_sum+=sum

print(total_sum)

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
