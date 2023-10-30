import sys
import ctypes
from ctypes import *
import os
import time
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import subprocess as sp



import sys


import pathosonicscannercontrol as pssc

multiscan = str(sys.argv[1])






with open("scanning","w") as fs:
	fs.write("1")




myp = os.path.dirname(__file__) + os.sep


# Path to script
myp = os.path.dirname(__file__) + os.sep
print("My path: ",myp)

ts_measurement = int(time.time())
ts_measurement_fatemeh = str(datetime.fromtimestamp (ts_measurement)).replace(":","").replace(" ","_").replace("-","")
print(ts_measurement_fatemeh,ts_measurement)
measurement_directory  =myp +os.sep+"static"+os.sep + "data"+ os.sep+ str(ts_measurement_fatemeh)
os.mkdir(measurement_directory)




#configuration
w = 512*2

h = 512*2


travel_speed_x = 0.5 	# mm/s scanner
e_r = 0.06				#mm - elevation resolution required
dx = 118 				#mm - probe sampling distance - X axis - scanner

frame_rate_aim =  25 #hz
sample_time =  1000.0/ frame_rate_aim # Milliseconds

time_interval_sampling_actual = sample_time

time_interval_sampling = e_r / travel_speed_x 	#Required to match e_r 
min_required_frames = int(round(dx / e_r)) 					# Minimum required frames to satisfy e_r conferning dx

correction_factor_sampling = time_interval_sampling / time_interval_sampling_actual

total_samples = min_required_frames 


myposition = pssc.get_position()[0]

with open(measurement_directory+os.sep+"config.txt",'a') as ffff: # could we add a header here?FM
	ffff.write("%s:%s;\n" % ("W",w))
	ffff.write("%s:%s;\n" % ("H",h))
	ffff.write("%s:%s;\n" % ("e_r setpoint",e_r))
	ffff.write("%s:%s;\n" % ("dx",dx))
	ffff.write("%s:%s;\n" % ("total_samples",total_samples))
	ffff.write("%s:%s;\n" % ("frame_rate_aim",frame_rate_aim))
	ffff.write("%s:%s;\n" % ("delay at SS",9)) #UPDATE CIONFIG when changed in MAIN
	ffff.write("%s:%s;\n" % ("scan speed ",90)) # mm/min (25hz and e_r) UPDATE CIONFIG when changed in pathosonicscannercontrol.py
	ffff.write("%s:%s;\n" % ("ID ",measurement_directory.split(os.sep)[-1])) 
	ffff.write("%s:%s;\n" % ("POSTIONS ",myposition.split("\n")[0]))  # could we have positions in a column as well?



#total_samples = min_required_frames * 3



print("min frames",min_required_frames)
print("time_interval_sampling",time_interval_sampling)
print("correction_factor_sampling",correction_factor_sampling)
print("Sampling: ", total_samples)


n_samples = int(round(total_samples))
#n_samples = 500





with open("recdir",'w') as f: f.write("%s" % (measurement_directory))

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

p_array = (ctypes.c_uint32*w*h*4)()

t_list = []


with open(measurement_directory+os.sep+"config.txt",'a') as ffff:
	ffff.write("%s:%s;\n" % ("Xres",old_resolution_x))
	ffff.write("%s:%s;\n" % ("Yres",old_resolution_y))


for i in range(0,n_samples):
	start_time = time.time()  #Start loop
	iteration = iteration+1

	usgfw2.return_pixel_values(ctypes.pointer(p_array)) #Get pixels

	buffer_as_numpy_array = np.frombuffer(p_array,np.uint32)
	#buffer_as_numpy_array = np.frombuffer(p_array, np.uint32)  
	reshaped_array = np.reshape(buffer_as_numpy_array,(w, h, 4))

	usgfw2.get_resolution(ctypes.pointer(res_X),ctypes.pointer(res_Y)) #Get resolution

	np.save(measurement_directory+ os.sep + str(i) , reshaped_array[:,:,0].astype(np.uint32))

	if i % 10 == 0: print(i)

	#im = Image.fromarray(myframe, mode='F') # float32
	#im.save(measurement_directory+ os.sep + str(i) + ".tiff", "TIFF")

	#im = Image.fromarray(myframe) # float32
	#im.save(measurement_directory+ os.sep + str(i)+"_"+str(int(start_time*1000)) + ".png")
	endtime = time.time()
	
	deltatime = (endtime - start_time)*1000
	#print(sample_time-deltatime,deltatime,start_time-time.time())
	try:
		time.sleep((sample_time - deltatime)/1000)
	except ValueError:
		continue

	t_list.append((time.time()-start_time)*1000)


	#, cmax=...





usgfw2.Freeze_ultrasound_scanning()
usgfw2.Stop_ultrasound_scanning()


try:
	usgfw2.Close_and_release() 
except:
	pass
#t_list = np.array(t_list)
sp.Popen(["py", myp + os.sep + "imconv.py"]) # This one changes scanning file to 0 when ended

print(np.mean(t_list),np.std(t_list))


del usgfw2


