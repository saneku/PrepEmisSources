import subprocess
import os
import json
import time
import numpy as np
from netCDF4 import Dataset
from scipy import sparse

#Set common paths
testpath = os.path.dirname(os.path.abspath(__file__))
datapath = os.path.abspath(os.path.join(testpath, "data"))
basepath = os.path.abspath(os.path.join(testpath, "..", ".."))


a_posteriori = os.path.join(datapath, 'inversion_000_1.00000000_a_posteriori.json')

reference='/Users/ukhova/Downloads/inversion_000_1.00000000_a_posteriori_reference.json'

with open(reference, 'r') as infile:
    a_priori_reference = json.load(infile)


#Compare important variables
#keys = ['level_boundaries', 'level_heights', 'volcano_altitude', 'a_priori_2d', 'a_priori_2d_uncertainty']
keys = ['a_posteriori_2d', 'level_heights', 'volcano_altitude', 'a_posteriori_2d','emission_times','ordering_index']
for key in keys:
    print(a_priori_reference[key])
