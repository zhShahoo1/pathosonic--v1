import sys
import ctypes
from ctypes import *
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.pyplot import imshow, show, draw, pause
import time

w = 512
h = 512

#usgfw2 = cdll.LoadLibrary('D:/DARBAS/Real_time_matlab/usgfw2matlab_sources/usgfw2MATLAB/x64/Release/usgfw2MATLAB_wrapper.dll') 
usgfw2 = cdll.LoadLibrary(r'C://Users//CAMES VR 3//Downloads//PCULTRASOUND//Real-time_imaging_for_the_research//usgfw2wrapper_C++_sources//usgfw2wrapper//x64//Release//usgfw2wrapper.dll') 

usgfw2.on_init()
ERR = usgfw2.init_ultrasound_usgfw2()

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

        
old_resolution_x = res_X.value;
old_resolution_y = res_X.value; 
print(old_resolution_y,old_resolution_x)

iteration = 0; 
run_loop = 1;
threshold = 500; 

p_array = (ctypes.c_uint*w*h*4)()

fig, ax = plt.subplots()
usgfw2.return_pixel_values(ctypes.pointer(p_array))
buffer_as_numpy_array = np.frombuffer(p_array, np.uint)  
reshaped_array = np.reshape(buffer_as_numpy_array,(w, h, 4))

img = ax.imshow(reshaped_array[:,:,0:3], cmap="gray",vmin=0, vmax=255,origin='lower',
                 extent =[np.amin(X_axis), np.amax(X_axis), np.amax(Y_axis), np.amin(Y_axis)])
plt.xlabel('Width [mm]')
plt.ylabel('Depth [mm]')





while (run_loop==1):

 start_time = time.time()  
 iteration = iteration+1
 usgfw2.return_pixel_values(ctypes.pointer(p_array))
 buffer_as_numpy_array = np.frombuffer(p_array, np.uint)  
 reshaped_array = np.reshape(buffer_as_numpy_array,(w, h, 4))

 usgfw2.get_resolution(ctypes.pointer(res_X),ctypes.pointer(res_Y))
 if (res_X.value!=old_resolution_x or res_Y.value!=old_resolution_y):
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

    old_resolution_x = res_X.value;
    old_resolution_y = res_X.value; 

 img.set_data(reshaped_array[:,:,0:3])
 img.set_extent([np.amin(X_axis), np.amax(X_axis), np.amax(Y_axis), np.amin(Y_axis)])

 plt.draw()
 pause(1e-8)

 plt.title('FPS = ' + str(round(1/(time.time() - start_time))))
 
 if (iteration > threshold):
      run_loop = 0;
      usgfw2.Freeze_ultrasound_scanning()
      usgfw2.Stop_ultrasound_scanning()
      usgfw2.Close_and_release() 

del usgfw2
