import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d
def drawTropopause(plt):
	plt.axhline(y=16.5, linestyle=':',color='black',linewidth=1.0)

def print_vector(vector,sep=' ',f="{:0.6e}"):
	print((sep.join(f.format(x) for x in vector)))

ex_factor=2000.0*1000.0
so2_ex_factor=ex_factor*4.0
CB_LABEL_TEXT_SIZE=15
TITLE_TEXT_SIZE=CB_LABEL_TEXT_SIZE+3
TICKS_TEXT_SIZE=CB_LABEL_TEXT_SIZE-3

#Height's of the model level's centers (meters above sea level A.S.L.):  (54,)
heights_on_levels=np.array([91.56439, 168.86765, 273.9505, 407.21893, 574.90356, 788.33356, 1050.1624, 1419.9668, 1885.3608, 2372.2937, 2883.3193, 3634.4663, 4613.3403, 5594.8545, 6580.381, 7568.5386, 8558.1455, 9547.174, 10534.043, 11518.861, 12501.9375, 13484.473, 14454.277, 15393.3125, 16300.045, 17189.598, 18083.797, 18998.496, 19939.57, 20905.723, 21890.363, 22886.46, 23890.441, 24900.914, 25918.307, 26943.252, 27977.344, 29021.828, 30077.21, 31143.973, 32221.8, 33310.13, 34408.86, 35517.9, 36637.133, 37766.45, 38905.723, 40054.82, 41213.594, 42381.883, 43559.504, 44746.254, 45941.914, 47146.22])
heights_on_levels_km=heights_on_levels/1000.0

#dz of model levels (meters)
dz_of_model_levels=np.array([63.175426, 91.43107, 118.734634, 147.80225, 187.56696, 239.29309, 284.36438, 455.2445, 475.54382, 498.32178, 523.72925, 978.5652, 979.1826, 983.8462, 987.20654, 989.1084, 990.10547, 987.9502, 985.78906, 983.8467, 982.3076, 982.7627, 956.8447, 921.22656, 892.2383, 886.86523, 901.53516, 927.8633, 954.28516, 978.0176, 991.2637, 1000.9336, 1007.02734, 1013.9199, 1020.8633, 1029.0273, 1039.1582, 1049.8066, 1060.9609, 1072.5605, 1083.0996, 1093.5547, 1103.9102, 1114.1641, 1124.3047, 1134.3281, 1144.2188, 1153.9766, 1163.5742, 1173.0039, 1182.2344, 1191.2656, 1200.0508, 1208.5625])

#loading best ASH emission scenario matrix (Mt/sec)
best_emission_profiles="./ash_2d_emission_profiles"
print("Loading best ASH 2d_emission from: "+best_emission_profiles)
infile = open(best_emission_profiles,'rb')
ca,solution_ensemble_size,solution_emission_scenario,solution_year,solution_month,solution_day,solution_hour,solution_duration,solution_time_labels = pickle.load(infile,encoding='latin1')
#For python v3 use this line:
#ca,solution_ensemble_size,solution_emission_scenario,solution_year,solution_month,solution_day,solution_hour,solution_duration,solution_time_labels = pickle.load(infile, encoding='latin1')
infile.close()

#loading best SO2 emission scenario matrix (Mt/sec)
best_emission_profiles="./so2_2d_emission_profiles"
print("Loading best SO2 2d_emission from: "+best_emission_profiles)
infile = open(best_emission_profiles,'rb')
ca,so2_solution_ensemble_size,so2_solution_emission_scenario,so2_solution_year,so2_solution_month,so2_solution_day,so2_solution_hour,so2_solution_duration,so2_solution_time_labels = pickle.load(infile,encoding='latin1')	
#For python v3 use this line:
#ca,so2_solution_ensemble_size,so2_solution_emission_scenario,so2_solution_year,so2_solution_month,so2_solution_day,so2_solution_hour,so2_solution_duration,so2_solution_time_labels = pickle.load(infile, encoding='latin1')

infile.close()


print(solution_time_labels)
print_vector(solution_hour," ","{:0.3f}")
print_vector(solution_duration," ","{:0.0f}")




#=============
time_interp = np.arange(2, 16)  # New time points for interpolation

# Interpolating for each height level
interp_solution_emission_scenario = np.array([interp1d(solution_hour, solution_emission_scenario[j, :], kind='linear', fill_value="extrapolate")(time_interp) for j in range(solution_emission_scenario.shape[0])])
interp_so2_solution_emission_scenario = np.array([interp1d(solution_hour, so2_solution_emission_scenario[j, :], kind='linear', fill_value="extrapolate")(time_interp) for j in range(so2_solution_emission_scenario.shape[0])])

#=============

#Convert emission scenario matrix to Mt/(m*sec)
for i in np.arange(0,solution_emission_scenario.shape[1],1):
	solution_emission_scenario[:,i]=solution_emission_scenario[:,i]/dz_of_model_levels
	so2_solution_emission_scenario[:,i]=so2_solution_emission_scenario[:,i]/dz_of_model_levels

#===============================
# Print ash and so2 emission scenario matrix Mt/(m*sec)
print("\nASH")
for j in np.arange(len(heights_on_levels)-1,-1,-1):
	print_vector(solution_emission_scenario[j,:],sep=' ',f='{:0.6e}')

print("\nSO2")
for j in np.arange(len(heights_on_levels)-1,-1,-1):
	print_vector(so2_solution_emission_scenario[j,:],sep=' ',f='{:0.6e}')

#===============================

for i in np.arange(0,interp_solution_emission_scenario.shape[1],1):
	interp_solution_emission_scenario[:,i]=interp_solution_emission_scenario[:,i]/dz_of_model_levels
	interp_so2_solution_emission_scenario[:,i]=interp_so2_solution_emission_scenario[:,i]/dz_of_model_levels
 
 
print("\nINTERP ASH")
for j in np.arange(len(heights_on_levels)-1,-1,-1):
	print_vector(interp_solution_emission_scenario[j,:],sep=' ',f='{:0.6e}')

print("\nINTERP SO2")
for j in np.arange(len(heights_on_levels)-1,-1,-1):
	print_vector(interp_so2_solution_emission_scenario[j,:],sep=' ',f='{:0.6e}')
#===============================

sum_ash=0
sum_so2=0
inv_cumulative_emission_ash=np.zeros([solution_emission_scenario.shape[0]])
inv_cumulative_emission_so2=np.zeros([so2_solution_emission_scenario.shape[0]])

for i in np.arange(0,solution_emission_scenario.shape[1],1):
	sum_ash=sum_ash+np.sum(solution_emission_scenario[:,i]*solution_duration[i]*dz_of_model_levels)
	sum_so2=sum_so2+np.sum(so2_solution_emission_scenario[:,i]*so2_solution_duration[i]*dz_of_model_levels)

	#cumulative profiles
	inv_cumulative_emission_ash=inv_cumulative_emission_ash+solution_emission_scenario[:,i]*solution_duration[i]
	inv_cumulative_emission_so2=inv_cumulative_emission_so2+so2_solution_emission_scenario[:,i]*solution_duration[i]


#total emitted mass checks:
#print sum_ash
#print sum_so2
#print np.sum(inv_cumulative_emission_ash*dz_of_model_levels)
#print np.sum(inv_cumulative_emission_so2*dz_of_model_levels)
#===============================
#Plot best Ash profile
fig = plt.figure(figsize=(18,7))
for i in np.arange(0,solution_emission_scenario.shape[1],1):
	plt.plot(ex_factor*solution_emission_scenario[:,i]+solution_hour[i],heights_on_levels_km,'-',color='grey')
	

for i in np.arange(0,solution_emission_scenario.shape[1],1):
	plt.plot(ex_factor*interp_solution_emission_scenario[:,i]+time_interp[i],heights_on_levels_km,'-',color='red')


drawTropopause(plt)
plt.gca().yaxis.set_major_locator(plt.MultipleLocator(5))
plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(1))
plt.xticks(solution_hour.tolist(),solution_time_labels.tolist())  # Set text labels.

plt.ylim(0.0, 40)
plt.xlim(0.5, 15.5)
plt.yticks(fontsize=TICKS_TEXT_SIZE)
plt.xticks(fontsize=TICKS_TEXT_SIZE)

plt.xlabel('Time (UTC)',fontsize=CB_LABEL_TEXT_SIZE)
plt.ylabel('Height, (km)',fontsize=CB_LABEL_TEXT_SIZE)
plt.title('A posteriori ash emission profiles ($Mt\ m^{-1} sec^{-1}$). Total ash emission '+"{:1.2f}".format(sum_ash)+' Mt',fontsize=TITLE_TEXT_SIZE)

plt.grid(True,alpha=0.3)
plt.tight_layout()
plt.savefig('aposteriori_profile_ash.png')
#===============================#===============================#===============================
#Plot best SO2 profile
fig = plt.figure(figsize=(18,7))
for i in np.arange(0,solution_emission_scenario.shape[1],1):
	plt.plot(so2_ex_factor*so2_solution_emission_scenario[:,i]+so2_solution_hour[i],heights_on_levels_km,'-',color='blue')

drawTropopause(plt)
plt.gca().yaxis.set_major_locator(plt.MultipleLocator(5))
plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(1))
plt.xticks(solution_hour.tolist(),solution_time_labels.tolist())  # Set text labels.

plt.ylim(0.0, 40)
plt.xlim(0.5, 15.5)
plt.yticks(fontsize=TICKS_TEXT_SIZE)
plt.xticks(fontsize=TICKS_TEXT_SIZE)

plt.xlabel('Time (UTC)',fontsize=CB_LABEL_TEXT_SIZE)
plt.ylabel('Height, (km)',fontsize=CB_LABEL_TEXT_SIZE)
plt.title('A posteriori $SO_2$ emission profiles ($Mt\ m^{-1} sec^{-1}$). Total $SO_2$ emission '+"{:1.2f}".format(sum_so2)+' Mt',fontsize=TITLE_TEXT_SIZE)

plt.grid(True,alpha=0.3)
plt.tight_layout()
plt.savefig('aposteriori_profile_so2.png')
#===============================#===============================#===============================
#===============================#===============================#===============================
#===============================#===============================#===============================
#PLOT Cumulative ash profile
fig = plt.figure(figsize=(7,7))
plt.gca().yaxis.set_major_locator(plt.MultipleLocator(5))
plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(1))

plt.plot(inv_cumulative_emission_ash,heights_on_levels_km,'-',markersize=0.5,color='grey')
plt.plot(inv_cumulative_emission_ash,heights_on_levels_km,marker='o',fillstyle='none',color='grey')

cumul_distribution=100.0*np.cumsum(inv_cumulative_emission_ash)/sum(inv_cumulative_emission_ash)

for i in np.arange(inv_cumulative_emission_ash.shape[0]):
	if(inv_cumulative_emission_ash[i]>0 and i<43):
		plt.text(inv_cumulative_emission_ash[i]+0.5e-4, (heights_on_levels_km)[i],"{:0.1f}".format(cumul_distribution[i])+"%",color='black', horizontalalignment='left',verticalalignment='top')

drawTropopause(plt)
plt.ylim(0.0, 40)
plt.xlim(0.0,0.03)
plt.ylabel('Height, (km)',fontsize=CB_LABEL_TEXT_SIZE)
plt.xlabel('Ash mass, ($Mt\ m^{-1}$)',fontsize=CB_LABEL_TEXT_SIZE)
plt.yticks(fontsize=TICKS_TEXT_SIZE)
plt.xticks(fontsize=TICKS_TEXT_SIZE)

plt.grid(True,alpha=0.3)
plt.tight_layout()
plt.savefig('ash_cumul.png')
#===============================#===============================#===============================
#PLOT Cumulative so2 profile
fig = plt.figure(figsize=(7,7))
plt.gca().yaxis.set_major_locator(plt.MultipleLocator(5))
plt.gca().yaxis.set_minor_locator(plt.MultipleLocator(1))

plt.plot(inv_cumulative_emission_so2,heights_on_levels_km,'-',markersize=0.5,color='blue')
plt.plot(inv_cumulative_emission_so2,heights_on_levels_km,marker='o',fillstyle='none',color='blue')

cumul_distribution=100.0*np.cumsum(inv_cumulative_emission_so2)/sum(inv_cumulative_emission_so2)

for i in np.arange(inv_cumulative_emission_so2.shape[0]):
	if(inv_cumulative_emission_so2[i]>0 and i<40):
		plt.text(inv_cumulative_emission_so2[i]+1e-4, (heights_on_levels_km)[i],"{:0.1f}".format(cumul_distribution[i])+"%",color='blue', horizontalalignment='left',verticalalignment='top')

drawTropopause(plt)
plt.ylim(0.0, 40)
plt.xlim(0.0,0.007)
plt.ylabel('Height, (km)',fontsize=CB_LABEL_TEXT_SIZE)
plt.xlabel('$SO_2$ mass, ($Mt\ m^{-1}$)',fontsize=CB_LABEL_TEXT_SIZE)
plt.yticks(fontsize=TICKS_TEXT_SIZE)
plt.xticks(fontsize=TICKS_TEXT_SIZE)

plt.grid(True,alpha=0.3)
plt.tight_layout()
plt.savefig('so2_cumul.png')