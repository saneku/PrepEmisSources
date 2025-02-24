from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import quad

x=20
y=20 

'''
#for another_suzuki_integrand
lambd=5.0
A=4.0

def another_suzuki_integrand(z):
	return pow((1.0-(z/H))*np.exp(A*((z/H)-1.0)),lambd)
'''

#for Suzuki integrand
#k=12.0
H=20.0 #top height of the cloud

def suzuku_integrand(z):
	return (k*k*(1-(z/H))*np.exp(k*((z/H)-1)))/(H*(1-(1+k)*np.exp(-k)))

#===========================================
#Read wrfinput
orgn_dir='/scratch/ukhova/SandBox/WRF/run_pinatubo_3days/'
orgn_wrf_input_file="wrfinput_d01"

print (f'Open {orgn_dir}{orgn_wrf_input_file}')
wrfinput=Dataset(f'{orgn_dir}{orgn_wrf_input_file}','r')
MAPFAC_MX=wrfinput.variables['MAPFAC_MX'][0,:]
MAPFAC_MY=wrfinput.variables['MAPFAC_MY'][0,:]
dy = wrfinput.getncattr('DY')
dx = wrfinput.getncattr('DX')
area = (dx/MAPFAC_MX)*(dy/MAPFAC_MY)       #cell surface area in m2

z_at_w = (wrfinput.variables['PH'][0,:] + wrfinput.variables['PHB'][0,:]) / 9.81  #meters
z_at_w = z_at_w[:,y,x]/1000.0

dz = np.diff(z_at_w,axis=0)
Z = z_at_w[:-1]
Z = Z + dz * 0.5
z_at_w=np.asarray(z_at_w)
wrfinput.close()

for k in np.array([4,8,12]):
    x_b=[]
    for i in range(0,len(z_at_w)-1):        
        bs, err = quad(suzuku_integrand, z_at_w[i],z_at_w[i+1])
        x_b.append(bs)

    x_b=np.asarray(x_b)
    indexes=np.where(x_b<0)
    x_b[indexes]=1.0e-06
    print (np.sum(x_b))

    #x_b_max=H*(k-1)/k
    #plt.axhline(x_b_max,label=f'x_b_max={x_b_max}')
    plt.plot(x_b,Z,".-",label=f'Suzuki: H={H} k={k}',linewidth=1.5)

axes = plt.gca()
axes.set_ylim([0,30])
axes.set_xlim(0,0.2)
#axes.set_xscale('log')

plt.grid(True)
plt.title("Mass Fractions for Suzuki profile")
#plt.xlabel('Vertical ash distribution')
plt.xlabel('Fraction',fontsize=10)
plt.ylabel('Altitude ,km',fontsize=10)
plt.legend(loc="best")
###########################
plt.grid(True)
plt.savefig('./profile_suzuki.png')