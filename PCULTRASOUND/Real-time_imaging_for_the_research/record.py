import sys
import ctypes
from ctypes import *

import time


import matplotlib.pyplot as plt

import numpy as np

from PIL import Image


import os

#configuration
w = 512
h = 512


travel_speed_x = 10 # mm/s scanner
e_r = 0.06 #mm - elevation resolution required
dx = 60 #mm - probe sampling distance - X axis - scanner
time_interval_sampling_actual = 2.9

time_interval_sampling = e_r / travel_speed_x #Required to match e_r 
min_required_frames = dx / e_r # Minimum required frames to satisfy e_r conferning dx
correction_factor_sampling = time_interval_sampling / time_interval_sampling_actual
total_samples = min_required_frames * correction_factor_sampling

print("Samling: ", total_samples)
n_samples = total_samples

# Path to script
myp = os.path.dirname(__file__) + os.sep
print("My path: ",myp)

ts_measurement = int(time.time())
measurement_directory  =myp + str(ts_measurement)

os.mkdir(measurement_directory)


#Loading dll
#usgfw2 = cdll.LoadLibrary('D:/DARBAS/Real_time_matlab/usgfw2matlab_sources/usgfw2MATLAB/x64/Release/usgfw2MATLAB_wrapper.dll') 
usgfw2 = cdll.LoadLibrary(r'C://Users//CAMES VR 3//Downloads//PCULTRASOUND//Real-time_imaging_for_the_research//usgfw2wrapper_C++_sources//usgfw2wrapper//x64//Release//usgfw2wrapper.dll') 

usgfw2.on_init()
ERR = usgfw2.init_ultrasound_usgfw2()


#Error handling
#------------------------------------------
if (ERR == 2):
	 print('Main Usgfw2 library object not created');
	 usgfw2.Close_and_release() 
	 sys.exit()
	 
ERR = usgfw2.find_connected_probe()

if (ERR != 101):
	 print('Probe not detected')
	 usgfw2.Close_and_release()
	 sys.exit()

ERR = usgfw2.data_view_function()

if (ERR < 0):
	print('Main ultrasound scanning object for selected probe not created')
	sys.exit()
	

ERR = usgfw2.mixer_control_function(0,0,w,h,0,0,0)
if (ERR < 0):
	print('B mixer control not returned');
	sys.exit()
	

#------------------------------------------

#Initialization
#------------------------------------------

res_X = ctypes.c_float(0.0)
res_Y = ctypes.c_float(0.0)
usgfw2.get_resolution(ctypes.pointer(res_X),ctypes.pointer(res_Y))


X_axis = np.zeros(shape=(w));
Y_axis = np.zeros(shape=(h));


if (w % 2 == 0): 

	k = 0;
	for i in range (-w//2, w//2+1):
		if (i<0):
			j=i+0.5
			X_axis[k] = j*res_X.value          
			k = k+1           
		else:
			if (i>0):
				j=i-0.5
				X_axis[k] = j*res_X.value             
				k = k+1
	  
else:
	for i in range (-w//2, w//2):
		X_axis[i+w/2 + 1] = i*res_X.value

for i in range (0,h-1):
	Y_axis[i] = i*res_Y.value;

#------------------------------------------


old_resolution_x = res_X.value;
old_resolution_y = res_X.value; 
print(old_resolution_y,old_resolution_x)

iteration = 0; 
run_loop = 1;

threshold = 500; 

p_array = (ctypes.c_uint*w*h*4)()

t_list = []
for i in range(0,n_samples):
	start_time = time.time()  #Start loop
	iteration = iteration+1

	usgfw2.return_pixel_values(ctypes.pointer(p_array)) #Get pixels

	buffer_as_numpy_array = np.frombuffer(p_array, np.uint)  
	reshaped_array = np.reshape(buffer_as_numpy_array,(w, h, 4))



	usgfw2.get_resolution(ctypes.pointer(res_X),ctypes.pointer(res_Y)) #Get resolution


	#myframe = reshaped_array[:,:,0].copy().astype(np.uint8)

	#print(i,myframe.shape)
	np.save(measurement_directory+ os.sep + str(i) , reshaped_array[:,:,0].astype(np.uint8))


	#im = Image.fromarray(myframe, mode='F') # float32
	#im.save(measurement_directory+ os.sep + str(i) + ".tiff", "TIFF")

	#im = Image.fromarray(myframe) # float32
	#im.save(measurement_directory+ os.sep + str(i)+"_"+str(int(start_time*1000)) + ".png")
	endtime = time.time()
	t_list.append((endtime-start_time)*1000)

	#, cmax=...



usgfw2.Freeze_ultrasound_scanning()
usgfw2.Stop_ultrasound_scanning()
usgfw2.Close_and_release() 

t_list = np.array(t_list)

print(np.mean(t_list),np.std(t_list))


del usgfw2
