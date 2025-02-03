import matplotlib.pyplot as plt
import numpy as np
from scipy.integrate import quad
from config import *

#for another_suzuki_integrand
lambd=5.0
A=4.0

#for Suzuki integrand
k=12.0
H=30.0 #top height of the cloud
x_b_max=H*(k-1)/k

def another_suzuki_integrand(z):
	return pow((1.0-(z/H))*np.exp(A*((z/H)-1.0)),lambd)

def suzuku_integrand(z):
	return (k*k*(1-(z/H))*np.exp(k*((z/H)-1)))/(H*(1-(1+k)*np.exp(-k)))

z=np.asarray(heights_on_levels)
z=z/1000
dz=np.diff(z)
z_mid=z[:-1]+dz*0.5

fig = plt.figure(figsize=(5,16))
for k in np.array([4,8,12]):
	x_b=[]
	for i in range(0,len(z)-1):        
	   bs, err = quad(suzuku_integrand, z[i],z[i+1])
	   x_b.append(bs)

	x_b=np.asarray(x_b)
	indexes=np.where(x_b<0)
	x_b[indexes]=1.0e-06
	print (np.sum(x_b))

	#plt.axhline(x_b_max)
	plt.plot(x_b,z_mid,".-",label='Suzuki: $H=$'+str(H)+'   $k=$'+str(k),linewidth=1.5)
	plt.xlabel('Vertical ash distribution')
	plt.ylabel('Height, km')


'''
x_b=another_suzuki_integrand(z_mid)
x_b=x_b/np.max(x_b)
indexes=np.where(x_b<0)
x_b[indexes]=1.0e-06

plt.plot(x_b,z_mid,".-",label='$\lambda=$'+str(lambd)+" A="+str(A),linewidth=1.5)
print (np.sum(x_b))
'''
plt.grid(True,alpha=0.3)
plt.tight_layout()
plt.legend()
plt.show()



'''
rates=np.logspace(3.0, 9.0, num=7)
h=2*pow(rates/rho,0.241)
plt.plot(rates,h,'-o')
plt.xscale('log')
plt.ylabel('Height, km')
plt.show()


h=np.linspace(0.0, 40.0, num=42)
rates=rho*pow(h/2,1/0.241)
plt.plot(h,rates,'-o')
plt.yscale('log')
plt.xlabel('Height, km')
plt.show()

exit()
'''