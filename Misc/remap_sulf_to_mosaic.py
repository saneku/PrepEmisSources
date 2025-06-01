import numpy as np
from pandas import *
from scipy.integrate import quad

def volume_integrand(r):
    mu = np.log(r2)
    sigma = np.log(sigma2)
    return (r**2)*(np.exp(-(np.log(r) - mu)**2 / (2 * sigma**2))/(sigma * np.sqrt(2 * np.pi)))

#Parameters of Aitken mode 
r1 = 0.09       # Aitken mode median radius  (um)
sigma1 = 1.4    # Aitken mode standard deviation

# Parameters of accumulation mode
r2 = 0.32      # Accumulation mode median radius (um)
sigma2 = 1.6    # Accumulation mode standard deviation

#grid with equal intervals on log-scale
dlo=0.0390625
dhi=10.0
nbin_o=8
nash=10

rlo_sectm=np.zeros(nbin_o)
rhi_sectm=np.zeros(nbin_o)

xlo = np.log( dlo )
xhi = np.log( dhi )
dxbin = (xhi - xlo)/nbin_o

print (str(nbin_o)+" MOZAIC BINS, radii")
dtemp=dlo
for n in range(0,nbin_o):
    rlo_sectm[n] = np.exp( xlo + dxbin*(n-1) )
    rhi_sectm[n] = np.exp( xlo + dxbin*n )

    print (n+1,"{:10.4f}".format(rlo_sectm[n]),"{:10.4f}".format(rhi_sectm[n]))


#comp
total_volume, _ = quad(volume_integrand, rlo_sectm[0], rhi_sectm[-1])

#initialize 8 bins. 
xmas_sect = np.zeros(nbin_o)
for n in range(0,nbin_o):
    xmas_sect[n], _ = quad(volume_integrand, rlo_sectm[n], rhi_sectm[n])
    xmas_sect[n] = xmas_sect[n]/total_volume

if not np.isclose(np.sum(xmas_sect), 1.0):
    raise ValueError(f"sum(xmas_sect)={np.sum(xmas_sect):0.2f} Should be =1.0")


print (DataFrame(xmas_sect))
print("Mass fractions of Sulfate in MOZAIC bins: " + (' '.join(str("{:.4f}".format(x)) for x in xmas_sect)))