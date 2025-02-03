#module load python/2.7.17-cdl
import matplotlib.pyplot as plt
import numpy as np
from config_so2 import *
import pickle
import pandas as pd

df = pd.read_csv('../Time_heigth.csv',names=['Date','Height'],header=None)#,parse_dates=True,index_col=0)
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

print df

print "Number of levels (rows) "+str(len(heights_on_levels))
print "Number of times (columns): "+str(len(df.index))

so2_apriori_emission_scenario=np.zeros([len(heights_on_levels),len(df.index)])
print "Creating so2_apriori_emission_scenario matrix size: ",so2_apriori_emission_scenario.shape

fig = plt.figure(figsize=(18,7))
ensemble_size=0
k=0
ensemble_index=0

rates=np.asarray(df['rates'])	#emission rates (kg/sec)
for h in np.asarray(df['Height']): #top heights of the cloud (km)
	H_suzuki=h


	#2 Uniform mass rate redistribution between 10km and observation heigth
	k_suzuki=0
	indexes=np.arange(getLayerIndexByHeigth(10000),getLayerIndexByHeigth(H_suzuki*1000),1)
	#indexes=np.arange(getLayerIndexByHeigth(15500),getLayerIndexByHeigth(H_suzuki*1000),1)
	#print indexes
	#print len(indexes)
	
	x_b_interp=np.zeros(len(heights_on_levels))
	x_b_interp[indexes]=rates[k]/len(indexes)
	print ("{:0.6f}".format(np.sum(x_b_interp)))

	ensemble_size=ensemble_size+len(indexes)

	#fill matrix
	#so2_apriori_emission_scenario[indexes,k]=x_b_interp[indexes]
	so2_apriori_emission_scenario[indexes,k]=total_mass/269.0
	#so2_apriori_emission_scenario[indexes,k]=total_mass/191.0
	k=k+1

#Scaling emissions to get desired total emitted so2 mass
scaled_apriori_emission_scenario=np.zeros(so2_apriori_emission_scenario.shape)
for i in np.arange(0,so2_apriori_emission_scenario.shape[1],1):
	scaled_apriori_emission_scenario[:,i]=so2_apriori_emission_scenario[:,i]*df['duration'][i]

scale_factor=total_mass/np.sum(scaled_apriori_emission_scenario)
so2_apriori_emission_scenario=so2_apriori_emission_scenario*scale_factor
print "ATTENTION!!! SO2 emission are scalled to "+str(total_mass)+" Mt"


for k in np.arange(0,so2_apriori_emission_scenario.shape[1],1):
	line,=plt.plot(ex_factor*so2_apriori_emission_scenario[:,k]+df['dec_hour'][k],heights_on_levels/1000.0,'o--',markersize=0.5)
	indexes=np.where(so2_apriori_emission_scenario[:,k]>0)
	plt.plot(ex_factor*so2_apriori_emission_scenario[:,k][indexes]+df['dec_hour'][k], (heights_on_levels/1000.0)[indexes],marker='o',fillstyle='none', color=plt.gca().lines[-1].get_color())

	for n in np.arange(so2_apriori_emission_scenario[:,k][indexes].shape[0]):
		plt.text((ex_factor*so2_apriori_emission_scenario[:,k])[n]+df['dec_hour'][k]-0.20, (heights_on_levels/1000.0)[indexes][n],str(ensemble_index),color=plt.gca().lines[-1].get_color(), horizontalalignment='center',verticalalignment='center')
		ensemble_index=ensemble_index+1
		plt.text((ex_factor*so2_apriori_emission_scenario[:,k])[n]+df['dec_hour'][k]+0.22, (heights_on_levels/1000.0)[indexes][n],indexes[0][n],color="black", horizontalalignment='right',verticalalignment='center',fontsize=6)


#####################################
print so2_apriori_emission_scenario.shape[0]
print so2_apriori_emission_scenario.shape[1]
print_vector(df['year'].values," ","{:0.0f}")
print_vector(df['month'].values," ","{:0.0f}")
print_vector(df['day'].values," ","{:0.0f}")
print_vector(df['dec_hour'].values," ","{:0.6f}")
print_vector(df['duration'].values," ","{:0.0f}")

for j in np.arange(len(heights_on_levels)-1,-1,-1):
	print_vector(so2_apriori_emission_scenario[j,:],sep=' ',f='{:0.6e}')
#####################################

#check that total emitted ash mass is equal to the desired
summa=0
cumulative_emission=np.zeros([so2_apriori_emission_scenario.shape[0]])
for i in np.arange(0,so2_apriori_emission_scenario.shape[1],1):
	summa=summa+np.sum(so2_apriori_emission_scenario[:,i]*df['duration'][i])

	#cumulative profile
	cumulative_emission=cumulative_emission+so2_apriori_emission_scenario[:,i]*df['duration'][i]
print summa


#Saving to disk
print "Saving profiles to "+emission_profiles
with open(emission_profiles,'wb') as wfp:
    pickle.dump((np.ones(ensemble_size),ensemble_size,so2_apriori_emission_scenario,df['year'].values,df['month'].values,df['day'].values,df['dec_hour'].values,df['duration'].values,df['time_labels'].values), wfp)
#####################################

plt.gca().yaxis.set_major_locator(plt.MultipleLocator(5))
plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(1))

plt.xticks(df['dec_hour'].tolist(), df['time_labels'].tolist())  # Set text labels.
drawTropopause(plt)
plt.xticks(fontsize=TICKS_TEXT_SIZE)
plt.yticks(fontsize=TICKS_TEXT_SIZE)
plt.ylim(0.0, 40)
plt.xlim(0.5, 15.5)
plt.xlabel("15 June 1991.",fontsize=CB_LABEL_TEXT_SIZE)#+str(ensemble_size)+" emission impulses")
plt.ylabel('Height, (km)',fontsize=CB_LABEL_TEXT_SIZE)
#plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
#plt.title('Vertical distribution of a priori ash emission rates (Mt/sec)')#' scalled to '+str(total_mass)+' Mt.')
plt.grid(True,alpha=0.3)
plt.tight_layout()
#plt.show()
plt.savefig('so2_apriori_profiles.png')


'''
#cumulative profile
fig = plt.figure(figsize=(7,7))
plt.title('Vertical distribution of cumulative a priori SO2 emission scalled to '+str(total_mass)+' Mt.')
plt.gca().yaxis.set_major_locator(plt.MultipleLocator(5))
plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(1))
plt.plot(cumulative_emission,heights_on_levels/1000.0,'o--',markersize=0.5,color='blue')
plt.plot(cumulative_emission,heights_on_levels/1000.0,marker='o',fillstyle='none',color='blue')
plt.ylim(0.0, 40)
plt.xlim(0.0,3.0)
plt.xlabel('Mass, (Mt)')
plt.ylabel('Height, (km)')
plt.grid(True,alpha=0.3)
plt.tight_layout()
plt.savefig('apriori_cum_profile.png')

os.system('convert so2_apriori_profiles.png apriori_cum_profile.png +append ./so2_apriori_profiles.png')
os.system('rm apriori_cum_profile.png')
'''
