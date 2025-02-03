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



'''
kts=0
kte=len(z_at_w)
#===========================================

ashz_above_vent = emiss_ash_height - z_at_w[kts]

for k in range(kte-1,kts,-1):
    if(z_at_w[k] < emiss_ash_height):
        k_final = k+1
        break

for k in range(kte-1,kts,-1):
    if(z_at_w[k] < ((1.-base_umbrel) * ashz_above_vent) + z_at_w[kts]):
        k_initial = k
        break

print(k_initial,k_final,kte)
print(emiss_ash_height,emiss_ash_mass,ashz_above_vent)

#- parabolic vertical distribution between k_initial and k_final
kk4 = k_final - k_initial+2
vert_mass_dist=np.zeros(len(z_at_w)-1)

for ko in range(1,kk4):
    kl = ko + k_initial - 1
    vert_mass_dist[kl] = 6. * percen_mass_umbrel * float(ko)/float(kk4)**2 * (1. - float(ko)/float(kk4))

#make sure that we put percen_mass_umbrel in 'umbrella'
if(sum(vert_mass_dist) != percen_mass_umbrel):
    x1= (percen_mass_umbrel - sum(vert_mass_dist)) /float(k_final-k_initial+1)
    for ko in range(k_initial,k_final+1):        
        vert_mass_dist[ko] = vert_mass_dist[ko]+ x1

#linear detrainment from vent to base of umbrella
for ko in range(0,k_initial):
    vert_mass_dist[ko]=float(ko)/float(k_initial-1)

#normalisation of sum of fractions of below umbrella
x1=sum(vert_mass_dist[0:k_initial])
for ko in range(0,k_initial):
    vert_mass_dist[ko]=(1.-percen_mass_umbrel) * vert_mass_dist[ko]/x1


print(vert_mass_dist)
print(sum(vert_mass_dist))
'''
