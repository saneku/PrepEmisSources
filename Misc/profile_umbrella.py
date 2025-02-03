from netCDF4 import Dataset
import numpy as np
import matplotlib.pyplot as plt

emiss_ash_height=15000
percen_mass_umbrel=0.75
base_umbrel=1.-percen_mass_umbrel
x=20
y=20 

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
z_at_w = z_at_w[:,y,x]

dz = np.diff(z_at_w,axis=0)
Z = z_at_w[:-1]
Z = Z + dz*0.5
#Z = Z/1000.0
z_at_w=np.asarray(z_at_w)
wrfinput.close()

#print(f"{i+1}. Volcano coordinates: ",volc_lats[i],volc_lons[i])
#y,x,d=findClosetGridPoint(xlat, xlon, volc_lats[i],volc_lons[i])

so2_mass = 1.5e4*3600.*1.e9/64./area[y,x]
eh = 2600.*(emiss_ash_height*.0005)**4.1494
emiss_ash_mass=eh*1.e9/area[y,x]


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

plt.plot(vert_mass_dist,Z/1000.0,'-+',label=f"Umbrella {percen_mass_umbrel}%, Base {base_umbrel}%, \nMax Emissions {emiss_ash_height/1000.0} km")

    
axes = plt.gca()
axes.set_ylim([0,30])
axes.set_xlim(0,0.2)
#axes.set_xscale('log')

plt.grid(True)
plt.title("Mass Fractions for umbrella profile")
plt.xlabel('Fraction',fontsize=10)
plt.ylabel('Altitude ,km',fontsize=10)
plt.legend(loc="best")
###########################
plt.grid(True)
plt.savefig('./profile_umbrella.png')
