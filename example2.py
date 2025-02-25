#from emissions.emissions import Emission_Ash, Emission_SO2, Emission_Sulfate, Emission_WaterVapor

from emissions import *

#from core.netcdf_handler import WRFNetCDFHandler
#from core.emission_scenario import EmissionScenario_InvertedPinatubo,EmissionScenario_MixOfProfiles
#from core.emission_writer import EmissionWriter

from core import *# WRFNetCDFHandler, EmissionScenario_InvertedPinatubo, EmissionScenario_MixOfProfiles, EmissionWriter
import numpy as np

if __name__ == "__main__":
    
    #example 2
    scenarios = [
                EmissionScenario_InvertedPinatubo(Emission_Ash(mass_mt=66.53,lat=15.1429,lon=120.3496,mean=2.4,stddev=1.8),
                                                    './example_profiles/Pinatubo_Ukhov_2023/ash_2d_emission_profiles'),

                EmissionScenario_InvertedPinatubo(Emission_SO2(mass_mt=15.54,lat=15.1429,lon=120.3496),
                                                     './example_profiles/Pinatubo_Ukhov_2023/so2_2d_emission_profiles')
                #Emission_Sulfate(mass_mt=0.1,lat=15,lon=165),
                #Emission_WaterVapor(mass_mt=150,lat=15,lon=165)
                ]
    #scenarios[0].plot(linestyle='--', color='grey', marker='')
    netcdf_handler = WRFNetCDFWriter(source_dir="./")
    
    emission_writer = EmissionWriter_NonUniformInTimeProfiles(scenarios, netcdf_handler, 10)
    emission_writer.write()
    
#todo:
#add check of emissions in wrfchem file
    
#todo    
#df['rates']=pow(df['Height']/2,1/0.241)	#formula (1) from Mastin 2009 (kg/s)
#df['rates']=df['rates']/df['rates'].max()	#normalise emission rates on max value. (kg/s)



'''
todo:
from scipy.integrate import quad

#for Suzuki integrand
k_suzuki=4.0
H_suzuki=0.0 #top height of the cloud

def suzuku_integrand(z):
	return (k_suzuki*k_suzuki*(1-(z/H_suzuki))*np.exp(k_suzuki*((z/H_suzuki)-1)))/(H_suzuki*(1-(1+k_suzuki)*np.exp(-k_suzuki)))



	#1 Vertical mass rate redistribution according to Suzuki
	x_b_interp=[]
	for i in range(0,len(heights_on_level_interfaces)-1):
	   bs, err = quad(suzuku_integrand, heights_on_level_interfaces[i]/1000.0,heights_on_level_interfaces[i+1]/1000.0)
	   x_b_interp.append(bs)
	x_b_interp=np.asarray(x_b_interp)

	x_b_interp=rates[k]*x_b_interp	#

	indexes=np.where(x_b_interp<0)
	x_b_interp[indexes]=1.0e-06
	print ("{:0.6f}".format(np.sum(x_b_interp)))

	indexes=np.where(x_b_interp>treshold)[0]
	'''