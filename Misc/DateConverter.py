import datetime
import numpy as np
from netCDF4 import Dataset

erup_year=1991
netcdf_file='/home/ukhova/Apps/WRF/V3.7.1/WRFV3.7.1/run_visuvi_tutorial/wrfchemv_d01'

fmt="%Y.%m.%d at %H:%M"
des_erup_end_date="1991.07.16 at 23:00"
#--------------------------------------------

print("Reading "+netcdf_file)
ncfile = Dataset(netcdf_file,'r+')

erup_beg = ncfile.variables["ERUP_BEG"][0,:,:]
i,j = np.unravel_index(erup_beg.argmax(), erup_beg.shape)
print("Found volcano at i="+str(i)+" j="+str(j))

erup_beg = ncfile.variables["ERUP_BEG"][0,i,j]
erup_end = ncfile.variables["ERUP_END"][0,i,j]


begday = int(erup_beg/1000)-1
beghr  = int(erup_beg)-(begday+1)*1000

endhr  = beghr+int(erup_end/60)
endday = int(begday+endhr/24)-1

erup_beg_date = datetime.datetime(erup_year, 1, 1) + datetime.timedelta(days=begday, hours=beghr)
erup_end_date = datetime.datetime(erup_year, 1, 1) + datetime.timedelta(days=endday, hours=endhr)

print("\nFound the following dates:")
print('Erup. beg: '+erup_beg_date.strftime(fmt))
print('Erup. end: '+erup_end_date.strftime(fmt))


print("\nDesirable Erup. end date is: "+des_erup_end_date)

des_erup_end=datetime.datetime.strptime(des_erup_end_date,fmt)

print('Duration of new eruption: '+str(((des_erup_end-erup_beg_date).days))+' days and ' +str(((des_erup_end-erup_beg_date).seconds/3600))+ ' hours')

des_erup_end=((des_erup_end-erup_beg_date).days) * 24 * 60+((des_erup_end-erup_beg_date).seconds/60)

cont = input("Do you want to update ERUP_END field in provided netcdf file ? [y/n] ")
if cont.lower() in ("y", "yes"):
    print("you entered", cont)
    print("Updating ERUP_END to "+str(des_erup_end)+"...")
    ncfile.variables["ERUP_END"][0,i,j]=des_erup_end

    print("File "+netcdf_file+" was updated.")
else:
    print("No changes to file "+netcdf_file+" has been made")

ncfile.close()
