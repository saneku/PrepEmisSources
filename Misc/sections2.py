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


#========================
#10 ash size bins
mu = np.log(2*2.4)  # 2.4 median radii!!!
sigma = np.log(1.8)

dlo_sect=[1e-5,3.90625,7.8125,15.625,31.25,62.5,125,250,500,1000]
dhi_sect=[3.90625,7.8125,15.625,31.25,62.5,125,250,500,1000,2000]
nbin=10
#========================


dlo_sect=np.array([0.2,2.0,3.6,6.0,10.0])
dhi_sect=np.array([2.0,3.6,6.0,12.0,20.0])
nbin=5


range_min=1e-10
range_max=1e5
total_volume, err = quad(volume_integrand, range_min, range_max)

xmas_sect=np.zeros(nbin)

for n in range(0,nbin):
    xmas_sect[n], err = quad(volume_integrand, dlo_sect[n], dhi_sect[n])
    xmas_sect[n] = xmas_sect[n]/total_volume

print ("MASS redistribution: "+(' '.join(str("{:.3f}".format(x)) for x in xmas_sect)))
print (np.sum(xmas_sect))

#Vash10, Vash9, Vash8, ...., Vash1
#1.726e-02 1.577e-01 4.216e-01 3.261e-01 7.262e-02 4.541e-03 7.733e-05 3.492e-07 4.103e-10 1.239e-13