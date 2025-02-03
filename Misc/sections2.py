import numpy as np
from scipy.integrate import quad

def volume_integrand(x):
    return (4.0*np.pi*(x**3)/3.0)*(np.exp(-(np.log(x) - mu)**2 / (2 * sigma**2))/(x * sigma * np.sqrt(2 * np.pi)))

#parameters of log-normal distribution
#Aitken mode 
mu = np.log(0.09)# radii!!!
sigma = np.log(1.4)

#Accumulation mode 
#mu = np.log(0.32)# radii!!!
#sigma = np.log(1.6)

#8 MOSAIC bin. radii based
dlo_sect=[0.01953125,0.0390625,0.078125,0.15625,0.3125,0.625,1.25,2.5]
dhi_sect=[0.03906250,0.0781250,0.156250,0.31250,0.6250,1.250,2.50,5.0]
nbin=8

range_min=0.01
range_max=100.0
total_volume, err = quad(volume_integrand, range_min, range_max)

xmas_sect=np.zeros(nbin)

for n in range(0,nbin):
    xmas_sect[n], err = quad(volume_integrand, dlo_sect[n], dhi_sect[n])
    xmas_sect[n] = xmas_sect[n]/total_volume

print ("MASS redistribution: "+(' '.join(str("{:.3e}".format(x)) for x in xmas_sect)))