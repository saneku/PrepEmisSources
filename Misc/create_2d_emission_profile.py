#module load python/2.7.17-cdl
import os
#import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('AGG')
import matplotlib.pyplot as plt


import numpy as np
from config import *
from scipy.interpolate import interp1d
import pickle
import pandas as pd
from scipy.integrate import quad

#for Suzuki integrand
k_suzuki=4.0
H_suzuki=0.0 #top height of the cloud

def suzuku_integrand(z):
	return (k_suzuki*k_suzuki*(1-(z/H_suzuki))*np.exp(k_suzuki*((z/H_suzuki)-1)))/(H_suzuki*(1-(1+k_suzuki)*np.exp(-k_suzuki)))


df = pd.read_csv('Time_heigth.csv',names=['Date','Height'],header=None)#,parse_dates=True,index_col=0)
df['Date'] = pd.to_datetime(df['Date'],format='%d/%m/%Y %H:%M')
df['Date'] = df['Date'].dt.tz_localize('Etc/GMT-9')
df['Date'] = df['Date'].dt.tz_convert('UTC')
df['Date_pdt'] = df['Date'].dt.tz_convert('Etc/GMT-9')

df['year'] = pd.DatetimeIndex(df['Date']).year
df['month'] = pd.DatetimeIndex(df['Date']).month
df['day'] = pd.DatetimeIndex(df['Date']).day
df['dec_hour']=pd.DatetimeIndex(df['Date']).hour + pd.DatetimeIndex(df['Date']).minute / 60.0
df['duration'] = ((df['Date'] - df['Date'].shift()).fillna(0).dt.seconds).shift(-1)

df['rates']=pow(df['Height']/2,1/0.241)	#formula (1) from Mastin 2009 (kg/s)
df['rates']=df['rates']/df['rates'].max()	#normalise emission rates on max value. (kg/s)

df=df.set_index('Date')
df=df.truncate(before=pd.Timestamp('1991-06-15'),after=pd.Timestamp('1991-06-15 23:00'))
df['duration'] = df['duration'].fillna(3600.0)
df=df.astype({"duration": int})

df['time_labels']=map(lambda n: str(n)[11:16], df.index.values)
#df['time_labels_pdt']=map(lambda n: str(n)[11:16], df['Date_pdt'].values)

#suzuki parameters
#A=4.0
#lambd=5.0
#z=np.linspace(0.0,50.0,1000) # from 0 to 50 km

print df

print "Number of levels (rows) "+str(len(heights_on_levels))
print "Number of times (columns): "+str(len(df.index))

apriori_emission_scenario=np.zeros([len(heights_on_levels),len(df.index)])
print "Creating apriori_emission_scenario matrix size: ",apriori_emission_scenario.shape

fig = plt.figure(figsize=(18,10))
ensemble_size=0
k=0
ensemble_index=0

rates=np.asarray(df['rates'])	#emission rates (kg/sec)
for h in np.asarray(df['Height']): #top heights of the cloud (km)
	H_suzuki=h
	#x_b=pow((1.0-(z/H))*np.exp(A*((z/H)-1.0)),lambd)
	#x_b=rates[k]*x_b/np.max(x_b)
	#indexes=np.where(x_b<0)
	#x_b[indexes]=1.0e-06


	#interpolate analytical profile to vertical grid, where cell centers heights are given
	#f = interp1d(z*1000,x_b) #convert to km's
	#x_b_interp = f(heights_on_levels)

	'''
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

	#2 Uniform mass rate redistribution between 10km and observation heigth
	k_suzuki=0
	indexes=np.arange(getLayerIndexByHeigth(10000),getLayerIndexByHeigth(H_suzuki*1000),1)
	#print indexes
	#print len(indexes)
	
	x_b_interp=np.zeros(len(heights_on_levels))
	x_b_interp[indexes]=rates[k]/len(indexes)
	print ("{:0.6f}".format(np.sum(x_b_interp)))

	ensemble_size=ensemble_size+len(indexes)

	'''
	#3 Uniform mass rate redistribution between 12km and 35km
	k_suzuki=0
	indexes=np.arange(getLayerIndexByHeigth(12000),getLayerIndexByHeigth(35000),1)
	#print indexes
	#print len(indexes)
	
	x_b_interp=np.zeros(len(heights_on_levels))
	x_b_interp[indexes]=rates[k]/len(indexes)
	print ("{:0.6f}".format(np.sum(x_b_interp)))
	'''


	#fill matrix
	#apriori_emission_scenario[indexes,k]=x_b_interp[indexes]
	apriori_emission_scenario[indexes,k]=total_mass/269.0
	k=k+1
	

#Scaling emissions to get desired total emitted ash mass
scaled_apriori_emission_scenario=np.zeros(apriori_emission_scenario.shape)
for i in np.arange(0,apriori_emission_scenario.shape[1],1):
	scaled_apriori_emission_scenario[:,i]=apriori_emission_scenario[:,i]*df['duration'][i]

scale_factor=total_mass/np.sum(scaled_apriori_emission_scenario)
apriori_emission_scenario=apriori_emission_scenario*scale_factor
print "ATTENTION!!! Emission are scalled to "+str(total_mass)+" Mt"


for k in np.arange(0,apriori_emission_scenario.shape[1],1):
	line,=plt.plot(ex_factor*apriori_emission_scenario[:,k]+df['dec_hour'][k],heights_on_levels/1000.0,'o--',markersize=0.9,color='black')
	indexes=np.where(apriori_emission_scenario[:,k]>0)
	plt.plot(ex_factor*apriori_emission_scenario[:,k][indexes]+df['dec_hour'][k], (heights_on_levels/1000.0)[indexes],
	marker='o',fillstyle='none', color=plt.gca().lines[-1].get_color())

	for n in np.arange(apriori_emission_scenario[:,k][indexes].shape[0]):
		#plt.text((ex_factor*apriori_emission_scenario[:,k])[n]+df['dec_hour'][k]-0.15,
		#(heights_on_levels/1000.0)[indexes][n],str(ensemble_index),color=plt.gca().lines[-1].get_color(),
		#horizontalalignment='center',verticalalignment='center',fontsize=15)

		#ensemble_index=ensemble_index+1

		if (k==3):
			#print (ex_factor*apriori_emission_scenario[:,k])[n]+df['dec_hour'][k]+0.35
			plt.text(6.2,
			(heights_on_levels/1000.0)[indexes][n],indexes[0][n],color="black", horizontalalignment='right',
			verticalalignment='center',fontsize=18)


#####################################
print "\n\nCOPY THE FOLLOWING INTO THE Ensemble_template/emissions_2d_profile.formatted"
print "-------------------------"
print apriori_emission_scenario.shape[0]
print apriori_emission_scenario.shape[1]
print_vector(df['year'].values," ","{:0.0f}")
print_vector(df['month'].values," ","{:0.0f}")
print_vector(df['day'].values," ","{:0.0f}")
print_vector(df['dec_hour'].values," ","{:0.6f}")
print_vector(df['duration'].values," ","{:0.0f}")

for j in np.arange(len(heights_on_levels)-1,-1,-1):
	print_vector(apriori_emission_scenario[j,:],sep=' ',f='{:0.6e}')
print "-------------------------"
print "COPY THIS MATRIX INTO THE Ensemble_template/emissions_2d_profile.formatted\n\n"
#####################################

#check that total emitted ash mass is equal to the desired
summa=0
cumulative_emission=np.zeros([apriori_emission_scenario.shape[0]])
for i in np.arange(0,apriori_emission_scenario.shape[1],1):
	summa=summa+np.sum(apriori_emission_scenario[:,i]*df['duration'][i])
	
	#cumulative profile
	cumulative_emission=cumulative_emission+apriori_emission_scenario[:,i]*df['duration'][i]
print summa


#Saving to disk
print "Saving profiles to "+emission_profiles
with open(emission_profiles,'wb') as wfp:
    pickle.dump((np.ones(ensemble_size),ensemble_size,apriori_emission_scenario,df['year'].values,df['month'].values,df['day'].values,df['dec_hour'].values,df['duration'].values,df['time_labels'].values), wfp)
#####################################

plt.gca().yaxis.set_major_locator(plt.MultipleLocator(5))
plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(1))

time_labels = [s.replace(':', '') for s in df['time_labels'].tolist()]

plt.xticks(df['dec_hour'].tolist(), time_labels,fontsize=TICKS_TEXT_SIZE)  # Set text labels.
plt.yticks(fontsize=TICKS_TEXT_SIZE)
drawTropopause(plt)
plt.ylim(0.0, 40)
plt.xlim(0.5, 15.5)
plt.xlabel("Time (UTC)",fontsize=CB_LABEL_TEXT_SIZE)#+str(ensemble_size)+" emission impulses")
plt.ylabel('Height, (km)',fontsize=CB_LABEL_TEXT_SIZE)
#plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#plt.title('Vertical distribution of a priori ash emission rates (Mt/sec)')#' scalled to '+str(total_mass)+' Mt.')
plt.grid(True,alpha=0.3)
plt.tight_layout()
#plt.show()


#PlotScaleBar(plt,np.max(apriori_emission_scenario),ex_factor)

plt.savefig('apriori_profiles.png',dpi=dpi_res)


'''
#cumulative profile
fig = plt.figure(figsize=(7,7))
plt.title('Vertical distribution of cumulative a priori ash emission scalled to '+str(total_mass)+' Mt.')
plt.gca().yaxis.set_major_locator(plt.MultipleLocator(5))
plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(1))
plt.plot(cumulative_emission,heights_on_levels/1000.0,'o--',markersize=0.5,color='grey')
plt.plot(cumulative_emission,heights_on_levels/1000.0,marker='o',fillstyle='none',color='grey')
plt.ylim(0.0, 40)
plt.xlim(0.0,14.0)
plt.xlabel('Mass, (Mt)')
plt.ylabel('Height, (km)')
plt.grid(True,alpha=0.3)
plt.tight_layout()
plt.savefig('apriori_cum_profile.png')

os.system('convert apriori_profiles.png apriori_cum_profile.png +append ./apriori_profiles.png')
os.system('rm apriori_cum_profile.png')
'''