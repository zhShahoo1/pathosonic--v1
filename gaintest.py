import tkinter
from tkinter import ttk
from tkinter import *
from tkinter import filedialog
from tkinter import Menu
import pdb; 
import struct
import os
import math
import scipy
import numpy
import matplotlib
import sys
import ctypes
from ctypes import *
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.pyplot import imshow, show, draw, pause
import time
from winreg import *
from datetime import datetime
from tkinter import filedialog
from tkinter import messagebox
import os

from PIL import Image
os.environ['SDL_HINT_WINDOWS_ENABLE_MESSAGELOOP'] = "0"

matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

window = Tk()
var1 = IntVar()
var2 = IntVar()
r1_v = IntVar()
r2_v = IntVar()
r3_v = IntVar()

r4_v = IntVar()
r5_v = IntVar()
r6_v = IntVar()
r7_v = IntVar()


window.title("Python Data Control")

width = round(0.65*window.winfo_screenwidth())
height = round(0.55*window.winfo_screenheight())

resolution=str(width)+'x'+str(height)

window.geometry(resolution)
window.resizable(False, False)

tabControl = ttk.Notebook(window)
  
tab1 = ttk.Frame(tabControl,width=round(0.45*width), height=round(0.9*height))
tab2 = ttk.Frame(tabControl,width=round(0.45*width), height=round(0.9*height))
tab3 = ttk.Frame(tabControl,width=round(0.45*width), height=round(0.9*height))
tab4 = ttk.Frame(tabControl,width=round(0.45*width), height=round(0.9*height))

  
tabControl.add(tab1, text ='B mode controls')
tabControl.add(tab2, text ='RF controls')
tabControl.add(tab3, text ='Cine control and RF data recording')
tabControl.add(tab4, text ='Settings')

tabControl.pack(expand = 1, fill ="x")
tabControl.place(x = round(width*0.525), y = round(0.01*height))

global stop_imaging
stop_imaging = 0
global AutoSC
AutoSC = 0
global bits
bits = 8
bits_label = ttk.Label(window, text = str(bits) + ' bits')
bits_label.place(x = 580, y = 555)
global stop_cine
stop_cine = 1

w = 512 # B image width
h = 512 # B image heigth

menu = Menu(window)
new_item = Menu(menu)
print(1)
global usgfw2
global RF_Row_to_show
global source_ID
usgfw2 = cdll.LoadLibrary(r'C://Users//CAMES VR 3//Downloads//ArtUs_RFDataControl_for-MATLAB_Python_LabVIEW//usgfw2wrapper.dll')
usgfw2_0 = cdll.LoadLibrary(r'C://Users//CAMES VR 3//Downloads//PCULTRASOUND//Real-time_imaging_for_the_research//usgfw2wrapper_C++_sources//usgfw2wrapper//x64//Release//usgfw2wrapper.dll') 

window.protocol("WM_DELETE_WINDOW", lambda arg=usgfw2: on_closing(arg))

def on_closing(usgfw2):
    if messagebox.askokcancel("Quit", "Do you want to quit ultrasound data acquisition?"):
        # error when probe not detected
        global stop_imaging
        global stop_cine
        stop_imaging = 1
        stop_cine = 0
        window.destroy()
        usgfw2.Close_and_release()
        del usgfw2


usgfw2.on_init()
ERR = usgfw2.init_ultrasound_usgfw2()



if (ERR == 2):
      print('Main Usgfw2 library object not created');
      sys.exit()
     
ERR = usgfw2.find_connected_probe()

if (ERR != 101):
     print('Probe not detected')
     print(ERR)
     sys.exit()

ERR = usgfw2.data_view_function()

if (ERR < 0):
      print('Main ultrasound scanning object for selected probe not created')
      sys.exit()
    
ERR = usgfw2.mixer_control_function(0,0,w,h,0,0,0) 
if (ERR < 0):
      print('B mixer control not returned');
      sys.exit()


#---------------Scan converter callback for B mode image acquisition ----
usgfw2.set_callback_scan_converter()
#---------------Frequency control--------------------------------------------

usgfw2.frequency_control()  
freq = c_int(0)
freq_no = c_long(0)

usgfw2.B_FrequencySetPrevNext(0, ctypes.pointer(freq), ctypes.pointer(freq_no));  

frequency = str((freq.value)/1000000);


#---------------Depth control--------------------------------------------
usgfw2.depth_control()
depth = ctypes.c_int(0)
usgfw2.DepthSetPrevNext(0, ctypes.pointer(depth))

#---------------Gain control--------------------------------------------



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

for i in range(0,50):
    start_time = time.time()  #Start loop
    iteration = iteration+1

    usgfw2.return_pixel_values(ctypes.pointer(p_array)) #Get pixels

    buffer_as_numpy_array = np.frombuffer(p_array,np.uint32)
    reshaped_array = np.reshape(buffer_as_numpy_array,(w, h, 4))

    usgfw2.get_resolution(ctypes.pointer(res_X),ctypes.pointer(res_Y)) #Get resolution

    np.save( str(i) , reshaped_array[:,:,0].astype(np.uint32))

    img = Image.fromarray(reshaped_array[:,:,0], "RGB")
    img.save(str(i)+".png")
    if i % 10 == 0: print(i)

    endtime = time.time()
    

    time.sleep(1)
    gain = ctypes.c_int(0+i*2)

    usgfw2.B_GainSetByIdx(70, ctypes.pointer(gain))
    img.show()

















#---------------Power control--------------------------------------------
usgfw2.power_control()  

power = ctypes.c_int(0)
usgfw2.B_PowerSetByIdx(20,ctypes.pointer(power)); 

#---------------Lines density control ----------------------------------
usgfw2.lines_density();  
lines_density = ctypes.c_int(0)
usgfw2.B_LinesDensitySetPrevNext(0, ctypes.pointer(lines_density)); 

# --------------- View area control--------------------------------------------
usgfw2.view_area()
view_area = ctypes.c_int(0)
view_area_direction = 5;
usgfw2.B_view_areaSetPrevNext(view_area_direction, ctypes.pointer(view_area)); 


# --------------- Focus control ----------------------------------------------
usgfw2.focus_control();

focal_depth = ctypes.c_int(0)
focal_zones_count = ctypes.c_int(0)
focal_zone_idx = ctypes.c_int(0)

usgfw2.B_FocusSetPrevNext(0, ctypes.pointer(focal_depth), ctypes.pointer(focal_zones_count), ctypes.pointer(focal_zone_idx)); 

# --------------- Steering angle control ----------------------------------------------
available_steering_angle = usgfw2.steering_angle()
if (available_steering_angle == 1):
  steering_angle = ctypes.c_int(0)
  usgfw2.B_SteeringAngleSetPrevNext(0, ctypes.pointer(steering_angle));

# --------------- Dynamic range control ----------------------------------------------
usgfw2.B_dynamic_range();  
dynamic_range = ctypes.c_int(0)
usgfw2.B_DynamicRangeSetPrevNext(0, ctypes.pointer(dynamic_range));

dynamic_range_name = ttk.Label(tab1, text = 'Dynamic Range, [dB]')
dynamic_range_name.place(x = 30, y = 380)
dynamic_range_label = ttk.Label(tab1, text = dynamic_range.value)
dynamic_range_label.place(x = 170, y = 400)

# --------------- Scan direction control ----------------------------------------------
usgfw2.image_orientation()  
usgfw2.ChangeScanDirection(0)  
# --------------- TGC control (1) ----------------------------------------------
usgfw2.TGC_control()  

TGC_depth1 = ctypes.c_int(0)
usgfw2.adjust_TGC(0, 50, ctypes.pointer(TGC_depth1));


# ------------- TGC control (2) ------------------------------------
TGC_depth2 = ctypes.c_int(0)
usgfw2.adjust_TGC(1, 60, ctypes.pointer(TGC_depth2));


# ------------- TGC control (3) ------------------------------------
TGC_depth3 = ctypes.c_int(0)
usgfw2.adjust_TGC(2, 60, ctypes.pointer(TGC_depth3));

global TGC3_label
TGC3_label = ttk.Label(tab1, text = str(60) + ' %,  ' + str(TGC_depth3.value) + ' mm')
TGC3_label.place(x = 400, y = 330)


# ------------- TGC control (4) ------------------------------------
TGC_depth4 = ctypes.c_int(0)
usgfw2.adjust_TGC(3, 60, ctypes.pointer(TGC_depth4));
global TGC4_label
TGC4_label = ttk.Label(tab1, text = str(60) + ' %,  ' + str(TGC_depth4.value) + ' mm')
TGC4_label.place(x = 400, y = 360)


# ------------- TGC control (5) ------------------------------------
TGC_depth5 = ctypes.c_int(0)
usgfw2.adjust_TGC(4, 60, ctypes.pointer(TGC_depth5));
global TGC5_label
TGC5_label = ttk.Label(tab1, text = str(60) + ' %,  ' + str(TGC_depth5.value) + ' mm')
TGC5_label.place(x = 400, y = 390)


# --------------- UsgQualProp_control ------------------------------------
usgfw2.UsgQualProp_control();  

# --------------- Scan type control ---------------------------------------
usgfw2.scan_type_control()  
usgfw2.turn_on_scan_type(0);  

# --------------- Wide view angle control --------------------------------
usgfw2.wide_view_angle();
wide_view_name = ttk.Label(tab1, text = 'Wide View Angle, [deg]')
wide_view_name.place(x = 340, y = 40)
WideView_angle_label = ttk.Label(tab1, text = str(5))
WideView_angle_label.place(x = 480, y = 60)

# ------------- Compound angle control -----------------------------------
usgfw2.compound_angle()
compound_angle = ctypes.c_int(0)
usgfw2.CompoundAngleSetPrevNext(0, ctypes.pointer(compound_angle))
compound_angle_name = ttk.Label(tab1, text = 'Compound Angle, [deg]')
compound_angle_name.place(x = 340, y = 90)
Compound_angle_label = ttk.Label(tab1, text = compound_angle.value)
Compound_angle_label.place(x = 480, y = 110)

# ------------- Compound frames control ----------------------------------
usgfw2.compound_frames_number()  
compound_frames = ctypes.c_int(0)
usgfw2.CompoundFramesSetPrevNext(0, ctypes.pointer(compound_frames));

compound_frames_num_name = ttk.Label(tab1, text = 'Compound Frames Num')
compound_frames_num_name.place(x = 340, y = 140)

Compound_frames_label = ttk.Label(tab1, text = compound_frames.value)
Compound_frames_label.place(x = 480, y = 160)

# -------------  Subframe index ----------------------------------
SubFrameIndex = ctypes.c_int(0)
usgfw2.CompoundSubframeSetPrevNext(0, ctypes.pointer(SubFrameIndex));
compound_frames_num_name = ttk.Label(tab1, text = 'Compound SubFrame')
compound_frames_num_name.place(x = 340, y = 190)

if (compound_frames.value<=SubFrameIndex.value):
 usgfw2.CompoundSubframeSetPrevNext(-(compound_frames.value-SubFrameIndex.value), ctypes.pointer(SubFrameIndex));

Compound_subframes_label = ttk.Label(tab1, text = SubFrameIndex.value)
Compound_subframes_label.place(x = 480, y = 210)


#--------------- RF stream control ---------------
depth_max = depth.value;

depth1 = ctypes.c_long(0)
depth2 = ctypes.c_long(0)
line1 = ctypes.c_long(0)
line2 = ctypes.c_long(0)
lines_number = ctypes.c_long(0)

usgfw2.RF_window_get(ctypes.pointer(depth1),ctypes.pointer(depth2),ctypes.pointer(line1),ctypes.pointer(line2),ctypes.pointer(lines_number))
print(7)

if (depth2.value == 0):
   #usgfw2.RF_data_controls()
   source_ID = 1;
   usgfw2.RF_Data_source_ID(source_ID)
   #usgfw2.RF_lines_get(ctypes.pointer(line1),ctypes.pointer(line2))
   #L1 = line1.value
   #L2 = line2.value
   #usgfw2.RF_window_set(round(depth_max*0.25),round(depth_max*0.75),round(0.25*(line2.value - line1.value)),round(0.75*(line2.value - line1.value)))

usgfw2.RF_window_get(ctypes.pointer(depth1),ctypes.pointer(depth2),ctypes.pointer(line1),ctypes.pointer(line2),ctypes.pointer(lines_number))

RF_Row_to_show =int(np.fix((line2.value - line1.value)/2))


usgfw2.set_callback_Sample_Grabber()
sampling_period_ns = ctypes.c_int(0)
usgfw2.get_sampling_period(ctypes.pointer(sampling_period_ns))

number_of_samples_in_window_for_beam = int(numpy.fix(2*((depth2.value-depth1.value)/1000)/1540/((sampling_period_ns.value)*1e-9)))

# ------------- Resolution frames control ----------------------------------
res_X = ctypes.c_float(0.0)
res_Y = ctypes.c_float(0.0)
usgfw2.get_resolution(ctypes.pointer(res_X),ctypes.pointer(res_Y))

X1pix1line_0 = ctypes.c_float(0.0);
Y1pix1line_0 = ctypes.c_float(0.0);
X2pix1line_0 = ctypes.c_float(0.0);
Y2pix1line_0 = ctypes.c_float(0.0);

usgfw2.convert_units_to_pixels(round((L2 - L1 + 1)/2),SubFrameIndex.value, 0, 10, ctypes.pointer(X1pix1line_0), ctypes.pointer(Y1pix1line_0), ctypes.pointer(X2pix1line_0), ctypes.pointer(Y2pix1line_0))

X_axis = np.zeros(shape=(w,1));
Y_axis = np.zeros(shape=(h,1));
if (w % 2 == 0):
     difference1 = w/2-0.5;
     difference2 = w/2-0.5;
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
          difference1 = w/2;
          difference2 = w/2; 
          for i in range (-w//2, w//2):
            X_axis[i+w/2 + 1] = i*res_X.value
for i in range (0,h-1):
           Y_axis[i] = i*res_Y.value - Y1pix1line_0.value*res_Y.value;
        
old_resolution_x = res_X.value;
old_resolution_y = res_X.value;

# ----------------- Cine loop control ------------------------------------
usgfw2.cine_loop_controls()  

#---------------Frequency buttons--------------------------------------------
def frequency_button_down(usgfw2, frequency_label):

    frequency_label.config(text="")
    usgfw2.B_FrequencySetPrevNext(-1, ctypes.pointer(freq), ctypes.pointer(freq_no));  
    frequency = str((freq.value)/1000000);

    if (len(frequency)>=3):
     if ((frequency[-1]) == '1'):
      frequency_label.config(text = frequency[:-1] + ' ITHI')
     elif ((frequency[-1]) == '2'):
      frequency_label.config(text = frequency[:-1] + ' THI')
     else:
      frequency_label.config(text = frequency)
    else:
      frequency_label.config(text = frequency)


def frequency_button_up(usgfw2, frequency_label):

    frequency_label.config(text="")
    usgfw2.B_FrequencySetPrevNext(+1, ctypes.pointer(freq), ctypes.pointer(freq_no));  
    frequency = str((freq.value)/1000000);

    if (len(frequency)>=3):
     if ((frequency[-1]) == '1'):
      frequency_label.config(text = frequency[:-1] + ' ITHI')
     elif ((frequency[-1]) == '2'):
      frequency_label.config(text = frequency[:-1] + ' THI')
     else:
      frequency_label.config(text = frequency)
    else:
      frequency_label.config(text = frequency) 

     
#---------------Depth buttons--------------------------------------------
def depth_button_down(usgfw2, depth_label):
   depth_label.config(text="")
   usgfw2.DepthSetPrevNext(-1, ctypes.pointer(depth))
   depth_label.config(text=depth.value)

   TGC1_label.config(text="")
   usgfw2.adjust_TGC(0, tgc_slider1.get(), ctypes.pointer(TGC_depth1));
   TGC1_label.config(text = str(tgc_slider1.get()) + ' %,  ' + str(TGC_depth1.value) + ' mm')

   TGC2_label.config(text="")
   usgfw2.adjust_TGC(1, tgc_slider2.get(), ctypes.pointer(TGC_depth2));
   TGC2_label.config(text = str(tgc_slider2.get()) + ' %,  ' + str(TGC_depth2.value) + ' mm')

   TGC3_label.config(text="")
   usgfw2.adjust_TGC(2, tgc_slider3.get(), ctypes.pointer(TGC_depth3));
   TGC3_label.config(text = str(tgc_slider3.get()) + ' %,  ' + str(TGC_depth3.value) + ' mm')

   TGC4_label.config(text="")
   usgfw2.adjust_TGC(3, tgc_slider4.get(), ctypes.pointer(TGC_depth4));
   TGC4_label.config(text = str(tgc_slider4.get()) + ' %,  ' + str(TGC_depth4.value) + ' mm')

   TGC5_label.config(text="")
   usgfw2.adjust_TGC(4, tgc_slider1.get(), ctypes.pointer(TGC_depth5));
   TGC5_label.config(text = str(tgc_slider5.get()) + ' %,  ' + str(TGC_depth5.value) + ' mm')
   
def depth_button_up(usgfw2, depth_label):
   depth_label.config(text="")
   usgfw2.DepthSetPrevNext(+1, ctypes.pointer(depth))
   depth_label.config(text=depth.value)

   TGC1_label.config(text="")
   usgfw2.adjust_TGC(0, tgc_slider1.get(), ctypes.pointer(TGC_depth1));
   TGC1_label.config(text = str(tgc_slider1.get()) + ' %,  ' + str(TGC_depth1.value) + ' mm')

   TGC2_label.config(text="")
   usgfw2.adjust_TGC(1, tgc_slider2.get(), ctypes.pointer(TGC_depth2));
   TGC2_label.config(text = str(tgc_slider2.get()) + ' %,  ' + str(TGC_depth2.value) + ' mm')

   TGC3_label.config(text="")
   usgfw2.adjust_TGC(2, tgc_slider3.get(), ctypes.pointer(TGC_depth3));
   TGC3_label.config(text = str(tgc_slider3.get()) + ' %,  ' + str(TGC_depth3.value) + ' mm')

   TGC4_label.config(text="")
   usgfw2.adjust_TGC(3, tgc_slider4.get(), ctypes.pointer(TGC_depth4));
   TGC4_label.config(text = str(tgc_slider4.get()) + ' %,  ' + str(TGC_depth4.value) + ' mm')

   TGC5_label.config(text="")
   usgfw2.adjust_TGC(4, tgc_slider1.get(), ctypes.pointer(TGC_depth5));
   TGC5_label.config(text = str(tgc_slider5.get()) + ' %,  ' + str(TGC_depth5.value) + ' mm')
   
#---------------Gain slider-------------------------------------------
def gain_slider_click(event):
     gain_label.config(text="") 
     usgfw2.B_GainSetByIdx(gain_slider.get(), ctypes.pointer(gain))  
     gain_label.config(text=gain.value)   

#---------------Power slider-------------------------------------------
def power_slider_click(event):
     power_label.config(text="")
     usgfw2.B_PowerSetByIdx(power_slider.get(),ctypes.pointer(power)); 
     power_label.config(text=power.value) 

#---------------Lines desnity buttons-----------------------------------
def lines_density_button_down(usgfw2, lines_density_label):

     usgfw2.B_LinesDensitySetPrevNext(-1, ctypes.pointer(lines_density)); 

     lines_density_label.config(text="")
     if (lines_density.value == 8):
       string_LD = 'Low';

     if (lines_density.value == 16):
       string_LD = 'Medium';

     if (lines_density.value == 22):
       string_LD = 'Standard S';

     if (lines_density.value == 24):
       string_LD = 'Standard';

     if (lines_density.value == 32):
       string_LD = 'High';

     lines_density_label.config(text=string_LD)
  

def lines_density_button_up(usgfw2, lines_density_label):

     usgfw2.B_LinesDensitySetPrevNext(+1, ctypes.pointer(lines_density)); 

     lines_density_label.config(text="")
     if (lines_density.value == 8):
       string_LD = 'Low';

     if (lines_density.value == 16):
       string_LD = 'Medium';

     if (lines_density.value == 22):
       string_LD = 'Standard S';

     if (lines_density.value == 24):
       string_LD = 'Standard';

     if (lines_density.value == 32):
       string_LD = 'High';

     lines_density_label.config(text=string_LD)


#---------------View area buttons-----------------------------------
def view_area_button_down(usgfw2, view_area_label):
     if (view_area.value > 50):
         view_area_label.config(text="")
         usgfw2.B_view_areaSetPrevNext(-1, ctypes.pointer(view_area)); 
         view_area_label.config(text=view_area.value)

def view_area_button_up(usgfw2, view_area_label):
     if (view_area.value < 100):
         view_area_label.config(text="")
         usgfw2.B_view_areaSetPrevNext(+1, ctypes.pointer(view_area)); 
         view_area_label.config(text=view_area.value)

#---------------Focus buttons-----------------------------------
def focal_depth_button_down(usgfw2, focal_depth_label):

    if (focal_zone_idx.value > 0):
       focal_depth_label.config(text="")
       usgfw2.B_FocusSetPrevNext(-1, ctypes.pointer(focal_depth), ctypes.pointer(focal_zones_count), ctypes.pointer(focal_zone_idx));
       focal_depth_label.config(text = focal_depth.value)

def focal_depth_button_up(usgfw2, focal_depth_label):
    
     if (focal_zone_idx.value < focal_zones_count.value-1):
       focal_depth_label.config(text="")
       usgfw2.B_FocusSetPrevNext(+1, ctypes.pointer(focal_depth), ctypes.pointer(focal_zones_count), ctypes.pointer(focal_zone_idx));
       focal_depth_label.config(text = focal_depth.value) 

#---------------Steering angle buttons------------------------------
def steering_angle_button_down(usgfw2, steering_angle_label):
       steering_angle_label.config(text="")
       usgfw2.B_SteeringAngleSetPrevNext(-1, ctypes.pointer(steering_angle));
       steering_angle_label.config(text=steering_angle.value)
       
def steering_angle_button_up(usgfw2, steering_angle_label):
       steering_angle_label.config(text="")
       usgfw2.B_SteeringAngleSetPrevNext(+1, ctypes.pointer(steering_angle));
       steering_angle_label.config(text=steering_angle.value)

#---------------Dynamic range buttons------------------------------
def dynamic_range_button_down(usgfw2, dynamic_range_label):
   dynamic_range_label.config(text="") 
   usgfw2.B_DynamicRangeSetPrevNext(-1, ctypes.pointer(dynamic_range));
   dynamic_range_label.config(text=dynamic_range.value)

def dynamic_range_button_up(usgfw2, dynamic_range_label):
   dynamic_range_label.config(text="")
   usgfw2.B_DynamicRangeSetPrevNext(+1, ctypes.pointer(dynamic_range));
   dynamic_range_label.config(text=dynamic_range.value)

#---------------Scan direction checkbox ------------------------------
def change_scan_dir():
    if (var1.get() == 1):
      usgfw2.ChangeScanDirection(1)  
    else:
      usgfw2.ChangeScanDirection(0)  

#---------------TGC 1 slider ------------------------------------------
def tgc1_slider_click(event):
      TGC1_label.config(text="")
      usgfw2.adjust_TGC(0, tgc_slider1.get(), ctypes.pointer(TGC_depth1));
      TGC1_label.config(text = str(tgc_slider1.get()) + ' %,  ' + str(TGC_depth1.value) + ' mm')

      
#---------------TGC 2 slider ------------------------------------------
def tgc2_slider_click(event):
      TGC2_label.config(text="")
      usgfw2.adjust_TGC(1, tgc_slider2.get(), ctypes.pointer(TGC_depth2));
      TGC2_label.config(text = str(tgc_slider2.get()) + ' %,  ' + str(TGC_depth2.value) + ' mm')
#---------------TGC 3 slider ------------------------------------------
def tgc3_slider_click(event):
      TGC3_label.config(text="")
      usgfw2.adjust_TGC(2, tgc_slider3.get(), ctypes.pointer(TGC_depth3));
      TGC3_label.config(text = str(tgc_slider3.get()) + ' %,  ' + str(TGC_depth3.value) + ' mm')
#---------------TGC 4 slider ------------------------------------------
def tgc4_slider_click(event):
      TGC4_label.config(text="")
      usgfw2.adjust_TGC(3, tgc_slider4.get(), ctypes.pointer(TGC_depth4));
      TGC4_label.config(text = str(tgc_slider4.get()) + ' %,  ' + str(TGC_depth4.value) + ' mm')
#---------------TGC 5 slider ------------------------------------------
def tgc5_slider_click(event):
      TGC5_label.config(text="")
      usgfw2.adjust_TGC(4, tgc_slider5.get(), ctypes.pointer(TGC_depth5));
      TGC5_label.config(text = str(tgc_slider5.get()) + ' %,  ' + str(TGC_depth5.value) + ' mm')

#---------------Radiobutton B Standard --------------------------------
def radiobutton1_clicked(usgfw2, lines_density_label):
     r2_v.set(0)
     r3_v.set(0)
     usgfw2.turn_on_scan_type(0)
     WideView_angle_button_minus.configure(state = 'disabled')
     WideView_angle_button_plus.configure(state = 'disabled')

     Compound_angle_button_minus.configure(state = 'disabled')
     Compound_angle_button_plus.configure(state = 'disabled')
     Compound_frames_button_minus.configure(state = 'disabled')
     Compound_frames_button_plus.configure(state = 'disabled')
     Compound_subframes_button_minus.configure(state = 'disabled')
     Compound_subframes_button_plus.configure(state = 'disabled')

     usgfw2.B_LinesDensitySetPrevNext(0, ctypes.pointer(lines_density)); 

     lines_density_label.config(text="")
     if (lines_density.value == 8):
       string_LD = 'Low';

     if (lines_density.value == 16):
       string_LD = 'Medium';

     if (lines_density.value == 22):
       string_LD = 'Standard S';

     if (lines_density.value == 24):
       string_LD = 'Standard';

     if (lines_density.value == 32):
       string_LD = 'High';

     lines_density_label.config(text=string_LD)

#---------------Radiobutton B WideView --------------------------------

def radiobutton2_clicked(usgfw2, lines_density_label):
     r1_v.set(0)
     r3_v.set(0)
     usgfw2.turn_on_scan_type(1)
     WideView_angle_button_minus.configure(state = 'normal')
     WideView_angle_button_plus.configure(state = 'normal')

     Compound_angle_button_minus.configure(state = 'disabled')
     Compound_angle_button_plus.configure(state = 'disabled')
     Compound_frames_button_minus.configure(state = 'disabled')
     Compound_frames_button_plus.configure(state = 'disabled')
     Compound_subframes_button_minus.configure(state = 'disabled')
     Compound_subframes_button_plus.configure(state = 'disabled')

     usgfw2.B_LinesDensitySetPrevNext(0, ctypes.pointer(lines_density)); 

     lines_density_label.config(text="")
     if (lines_density.value == 8):
       string_LD = 'Low';

     if (lines_density.value == 16):
       string_LD = 'Medium';

     if (lines_density.value == 22):
       string_LD = 'Standard S';

     if (lines_density.value == 24):
       string_LD = 'Standard';

     if (lines_density.value == 32):
       string_LD = 'High';

     lines_density_label.config(text=string_LD)


#---------------Radiobutton B Compound --------------------------------
def radiobutton3_clicked(usgfw2, lines_density_label):
     r1_v.set(0)
     r2_v.set(0)
     usgfw2.turn_on_scan_type(2)
     WideView_angle_button_minus.configure(state = 'disabled')
     WideView_angle_button_plus.configure(state = 'disabled')

     Compound_angle_button_minus.configure(state = 'normal')
     Compound_angle_button_plus.configure(state = 'normal')
     Compound_frames_button_minus.configure(state = 'normal')
     Compound_frames_button_plus.configure(state = 'normal')
     Compound_subframes_button_minus.configure(state = 'normal')
     Compound_subframes_button_plus.configure(state = 'normal')

     usgfw2.B_LinesDensitySetPrevNext(0, ctypes.pointer(lines_density)); 

     lines_density_label.config(text="")
     if (lines_density.value == 8):
       string_LD = 'Low';

     if (lines_density.value == 16):
       string_LD = 'Medium';

     if (lines_density.value == 22):
       string_LD = 'Standard S';

     if (lines_density.value == 24):
       string_LD = 'Standard';

     if (lines_density.value == 32):
       string_LD = 'High';
     lines_density_label.config(text=string_LD)


#--------------- B WideView Buttons --------------------------------
def  WideView_angle_button_down(usgfw2, WideView_angle_label):

    wide_view_angle = ctypes.c_int(0);
    usgfw2.WideViewAngleSetPrevNext(-1, ctypes.pointer(wide_view_angle)); 
    WideView_angle_label.config(text = str(wide_view_angle.value))     
def  WideView_angle_button_up(usgfw2, WideView_angle_label):
    wide_view_angle = ctypes.c_int(0);
    usgfw2.WideViewAngleSetPrevNext(+1, ctypes.pointer(wide_view_angle)); 
    WideView_angle_label.config(text = str(wide_view_angle.value))

#--------------- B Compound Buttons --------------------------------   
def Compound_angle_button_down(usgfw2, Compound_angle_label):
     usgfw2.CompoundAngleSetPrevNext(-1, ctypes.pointer(compound_angle))
     Compound_angle_label.config(text = str(compound_angle.value))
     
def Compound_angle_button_up(usgfw2, Compound_angle_label):    
     usgfw2.CompoundAngleSetPrevNext(+1, ctypes.pointer(compound_angle))
     Compound_angle_label.config(text = str(compound_angle.value))
   
def Compound_frames_button_down(usgfw2, Compound_frames_label, Compound_subframes_label):
    usgfw2.CompoundFramesSetPrevNext(-1, ctypes.pointer(compound_frames))
    if (compound_frames.value<=SubFrameIndex.value):
       usgfw2.CompoundSubframeSetPrevNext(-(compound_frames.value-SubFrameIndex.value), ctypes.pointer(SubFrameIndex))
    Compound_frames_label.config(text = str(compound_frames.value))
    Compound_subframes_label.config(text = str(SubFrameIndex.value))

def Compound_frames_button_up(usgfw2, Compound_frames_label, Compound_subframes_label):
    usgfw2.CompoundFramesSetPrevNext(+1, ctypes.pointer(compound_frames))
    Compound_frames_label.config(text = str(compound_frames.value))
   
def Compound_subframes_button_down(usgfw2, Compound_subframes_label):
    usgfw2.CompoundSubframeSetPrevNext(-1, ctypes.pointer(SubFrameIndex))
    Compound_subframes_label.config(text = str(SubFrameIndex.value))
def Compound_subframes_button_up(usgfw2, Compound_subframes_label):
    usgfw2.CompoundSubframeSetPrevNext(+1, ctypes.pointer(SubFrameIndex))
    Compound_subframes_label.config(text = str(SubFrameIndex.value))

#--------------- RF window buttons --------------------------------   

def RF_window_move_right(usgfw2):   
    usgfw2.RF_WindowMove(1, 0)

def RF_window_move_left(usgfw2):
    usgfw2.RF_WindowMove(-1, 0)

def RF_window_move_up(usgfw2):
    usgfw2.RF_WindowMove(0, -1)
    
def RF_window_move_down(usgfw2):
    usgfw2.RF_WindowMove(0, 1)

def RF_window_size_right(usgfw2):
    usgfw2.RF_WindowSize(1, 0)

def RF_window_size_left(usgfw2):
    usgfw2.RF_WindowSize(-1, 0)
    

def RF_window_size_up(usgfw2):
    #if ((depth2.value - depth1.value) == 32 and depth1.value!=0 or (depth2.value - depth1.value) == 33 and depth1.value==0 and depth1.value==0 or(depth2.value - depth1.value) == 66 and depth1.value!=0 or (depth2.value - depth1.value) == 67 and depth1.value==0):
    #  usgfw2.RF_WindowSize(0, 2)
    #else:
      usgfw2.RF_WindowSize(0, 1)

def RF_window_size_down(usgfw2):
    #if ((depth2.value - depth1.value) == 36 and depth1.value!=0 or (depth2.value - depth1.value) == 35 and depth1.value==0 or (depth2.value - depth1.value) == 70 and depth1.value!=0 or (depth2.value - depth1.value) == 69 and depth1.value==0):
    #   usgfw2.RF_WindowSize(0, -2)
    #else:
       usgfw2.RF_WindowSize(0, -1)

#--------------- RF line slider --------------------------------   

def RF_line_slider_click(event):

    global RF_Row_to_show
    
    RF_Row_to_show = RF_line_slider.get()
    usgfw2.RF_window_get(ctypes.pointer(depth1),ctypes.pointer(depth2),ctypes.pointer(line1),ctypes.pointer(line2),ctypes.pointer(lines_number))
    RF_line_slider_label.config(text = str(RF_Row_to_show+1)+ '/' + str(lines_number.value))

    if (btn1["state"] == DISABLED):
       X1pixRFline = ctypes.c_float(0.0)
       Y1pixRFline = ctypes.c_float(0.0)
       X2pixRFline = ctypes.c_float(0.0)
       Y2pixRFline = ctypes.c_float(0.0)
       Line = int(RF_Row_to_show + line1.value)
       usgfw2.convert_units_to_pixels(Line,SubFrameIndex.value, depth1.value, depth2.value, ctypes.pointer(X1pixRFline), ctypes.pointer(Y1pixRFline), ctypes.pointer(X2pixRFline), ctypes.pointer(Y2pixRFline))
       XRFline = [(X1pixRFline.value-difference1)*res_X.value, (X2pixRFline.value-difference1)*res_Y.value];
       YRFline = [Y1pixRFline.value*res_X.value, Y2pixRFline.value*res_Y.value];  
       RF_line.set_xdata(XRFline);
       RF_line.set_ydata(YRFline); 

       RF_data_to_show = RF_buffer_as_numpy_array[RF_Row_to_show*number_of_samples_in_window_for_beam+3:RF_Row_to_show*number_of_samples_in_window_for_beam + number_of_samples_in_window_for_beam]
       RFimg.set_xdata(RF_data_to_show)
       
       if (source_ID == 4):
         RF_data_to_show2 = RF_buffer_as_numpy_array[(number_of_samples_in_window_for_beam*lines_number.value) + (RF_Row_to_show*number_of_samples_in_window_for_beam+3):(number_of_samples_in_window_for_beam*lines_number.value)+RF_Row_to_show*number_of_samples_in_window_for_beam + number_of_samples_in_window_for_beam]
         RFimg2.set_xdata(RF_data_to_show2)
       
       plt1.draw()
       
print(88)
#--------------- RF source point --------------------------------   
def radiobutton_beamformer_output_clicked(usgfw2):
    r5_v.set(0)
    r6_v.set(0)
    r7_v.set(0)
    global source_ID
    source_ID = 1;
    usgfw2.RF_Data_source_ID(source_ID)
    
def radiobutton_TFC_poutput_clicked(usgfw2):
    r4_v.set(0)
    r6_v.set(0)
    r7_v.set(0)
    global source_ID
    source_ID = 2;
    usgfw2.RF_Data_source_ID(source_ID)

    
def radiobutton_apodization_output_clicked(usgfw2):
    r4_v.set(0)
    r5_v.set(0)
    r7_v.set(0)
    global source_ID
    source_ID = 3;
    usgfw2.RF_Data_source_ID(source_ID)


def radiobutton_hilbert_output_clicked(usgfw2):
    r4_v.set(0)
    r5_v.set(0)
    r6_v.set(0)
    global source_ID
    source_ID = 4;
    usgfw2.RF_Data_source_ID(source_ID)

def Autoscale():
    global AutoSC
    AutoSC = var2.get()

    if (AutoSC == 1):
        IQ_bits_rigth.config(state = 'disabled')
        IQ_bits_left.config(state = 'disabled')
    else:
        IQ_bits_rigth.config(state = 'normal')
        IQ_bits_left.config(state = 'normal')

    RF_data_to_show = RF_buffer_as_numpy_array[RF_Row_to_show*number_of_samples_in_window_for_beam+3:RF_Row_to_show*number_of_samples_in_window_for_beam + number_of_samples_in_window_for_beam]
    if (btn1["state"] == DISABLED):
     if (AutoSC == 1):
       ax[1].axis(xmin=np.amin(RF_data_to_show)-5, xmax = np.amax(RF_data_to_show)+5, ymin = number_of_samples_in_window_for_beam-1,ymax = 1) 
     else:
       ax[1].axis(xmin=-2**bits/2, xmax = 2**bits/2, ymin = number_of_samples_in_window_for_beam-1,ymax = 1)
       
     if (source_ID == 4):
       RF_data_to_show2 = RF_buffer_as_numpy_array[(number_of_samples_in_window_for_beam*lines_number.value) + (RF_Row_to_show*number_of_samples_in_window_for_beam+3):(number_of_samples_in_window_for_beam*lines_number.value)+RF_Row_to_show*number_of_samples_in_window_for_beam + number_of_samples_in_window_for_beam]
       RFimg2.set_xdata(RF_data_to_show2)
       if (AutoSC == 1):
         ax[2].axis(xmin=np.amin(RF_data_to_show2)-5, xmax = np.amax(RF_data_to_show2)+5, ymin = number_of_samples_in_window_for_beam-1,ymax = 1) 
       else:
         ax[2].axis(xmin=-2**bits/2, xmax = 2**bits/2, ymin = number_of_samples_in_window_for_beam-1,ymax = 1)
    plt1.draw()
        
def IQ_bits_up():
    global bits
    if (bits<17):
      bits = bits+1
    else:
      bits = 17
      
    bits_label.config(text = str(bits) + ' bits')

    RF_data_to_show = RF_buffer_as_numpy_array[RF_Row_to_show*number_of_samples_in_window_for_beam+3:RF_Row_to_show*number_of_samples_in_window_for_beam + number_of_samples_in_window_for_beam]
    if (btn1["state"] == DISABLED):
     if (AutoSC == 1):
       ax[1].axis(xmin=np.amin(RF_data_to_show)-5, xmax = np.amax(RF_data_to_show)+5, ymin = number_of_samples_in_window_for_beam-1,ymax = 1) 
     else:
       ax[1].axis(xmin=-2**bits/2, xmax = 2**bits/2, ymin = number_of_samples_in_window_for_beam-1,ymax = 1)
       
     if (source_ID == 4):
       RF_data_to_show2 = RF_buffer_as_numpy_array[(number_of_samples_in_window_for_beam*lines_number.value) + (RF_Row_to_show*number_of_samples_in_window_for_beam+3):(number_of_samples_in_window_for_beam*lines_number.value)+RF_Row_to_show*number_of_samples_in_window_for_beam + number_of_samples_in_window_for_beam]
       RFimg2.set_xdata(RF_data_to_show2)
       if (AutoSC == 1):
         ax[2].axis(xmin=np.amin(RF_data_to_show2), xmax = np.amax(RF_data_to_show2), ymin = number_of_samples_in_window_for_beam-1,ymax = 1) 
       else:
         ax[2].axis(xmin=-2**bits/2, xmax = 2**bits/2, ymin = number_of_samples_in_window_for_beam-1,ymax = 1)
    plt1.draw()

    
def IQ_bits_down():
    global bits
    if (bits>2):
      bits = bits-1
    else:
      bits = 2  
    bits_label.config(text = str(bits) + ' bits')

    RF_data_to_show = RF_buffer_as_numpy_array[RF_Row_to_show*number_of_samples_in_window_for_beam+3:RF_Row_to_show*number_of_samples_in_window_for_beam + number_of_samples_in_window_for_beam]
    if (btn1["state"] == DISABLED):
     if (AutoSC == 1):
       ax[1].axis(xmin=np.amin(RF_data_to_show)-5, xmax = np.amax(RF_data_to_show)+5, ymin = number_of_samples_in_window_for_beam-1,ymax = 1) 
     else:
       ax[1].axis(xmin=-2**bits/2, xmax = 2**bits/2, ymin = number_of_samples_in_window_for_beam-1,ymax = 1)
       
     if (source_ID == 4):
       RF_data_to_show2 = RF_buffer_as_numpy_array[(number_of_samples_in_window_for_beam*lines_number.value) + (RF_Row_to_show*number_of_samples_in_window_for_beam+3):(number_of_samples_in_window_for_beam*lines_number.value)+RF_Row_to_show*number_of_samples_in_window_for_beam + number_of_samples_in_window_for_beam]
       RFimg2.set_xdata(RF_data_to_show2)
       if (AutoSC == 1):
         ax[2].axis(xmin=np.amin(RF_data_to_show2)-5, xmax = np.amax(RF_data_to_show2)+5, ymin = number_of_samples_in_window_for_beam-1,ymax = 1) 
       else:
         ax[2].axis(xmin=-2**bits/2, xmax = 2**bits/2, ymin = number_of_samples_in_window_for_beam-1,ymax = 1)
    plt1.draw()

# ---- Cine controls ------------------------- 
def Play_cine():
    
    global stop_cine 
    stop_cine = 1 
    for i in range (start.value, end.value):

        
     if (stop_cine == 0):
       stop_cine = 1;
       break;

     Cine_frame_slider.set(i - start.value + 1)
     usgfw2.get_cine_frame(i) 
     Cine_loop_frames_label.config(text = str(Cine_frame_slider.get()) + '/' + str(end.value-start.value))
     matplotCanvas(window,ax, difference1,reshaped_array[:,:,0:3], X_axis, Y_axis, p_array, p1, p2, img, usgfw2, res_X, res_Y, fig, plt1, P1, P2, P3, P4, RF_Row_to_show, RFimg, RFimg2, FPS_label,Q_component_label, RF_window, RF_line, focal_depth_marker)
     pause(1/10)
  
def Stop_cine():
    global stop_cine
    stop_cine = 0;

def Cine_frame_slider_click(event):
   
    usgfw2.get_cine_frame(start.value + Cine_frame_slider.get()-1) 
    Cine_loop_frames_label.config(text = str(Cine_frame_slider.get()) + '/' + str(end.value-start.value))
    matplotCanvas(window,ax, difference1,reshaped_array[:,:,0:3], X_axis, Y_axis, p_array, p1, p2, img, usgfw2, res_X, res_Y, fig, plt1, P1, P2, P3, P4, RF_Row_to_show, RFimg, RFimg2, FPS_label,Q_component_label, RF_window, RF_line, focal_depth_marker)

def Go_to_frame_button_click():
    
   
    try:
     frame_num = int(Go_to_frame_editbox.get(1.0,END))       
    except ValueError:
     ctypes.windll.user32.MessageBoxW(None, u"Field is empty or enetered value is not number", u"Error", 0)
     return
    else:
     if (int(frame_num)<1 or (int(frame_num)>(end.value-start.value))):
      ctypes.windll.user32.MessageBoxW(None, u"Entered value outside cine loop limits", u"Error", 0)
      return
     
     usgfw2.get_cine_frame(start.value + int(frame_num) - 1)
     Cine_frame_slider.set(int(frame_num))
     Cine_loop_frames_label.config(text = str(int(frame_num)) + '/' + str(end.value-start.value))
     matplotCanvas(window,ax, difference1,reshaped_array[:,:,0:3], X_axis, Y_axis, p_array, p1, p2, img, usgfw2, res_X, res_Y, fig, plt1, P1, P2, P3, P4, RF_Row_to_show, RFimg, RFimg2, FPS_label,Q_component_label, RF_window, RF_line, focal_depth_marker)

# ---- RF data record controls ------------------------- 
def RF_Data_record_single_frame_button_click():
    PROBE_CODE = usgfw2.get_probe_code()
    PROBE =""
    
    aReg = ConnectRegistry(None, HKEY_LOCAL_MACHINE) 
    aKey = r"SOFTWARE\TELEMED\Usgfw2\Probes"

    aKey = OpenKey(aReg, aKey)
    
    try:
     i = 0
     while True:
         
        asubkey_name = EnumKey(aKey, i)
        i=i+1
        asubkey = OpenKey(aKey, asubkey_name)
        val = QueryValueEx(asubkey, "Device Code")
        if (int(val[0]) == PROBE_CODE):
           PROBE = asubkey_name       
    except WindowsError:
     # WindowsError: [Errno 259] No more data is available    
     pass

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    filename = dt_string[11:13] + '.' + dt_string[14:16] + '.' + dt_string[17:19] + '_' + dt_string[0:2] + '-' + dt_string[3:5] + '-' + dt_string[6:10] +'_' +PROBE +'.bin'
    file_path = filedialog.asksaveasfile(mode='w', defaultextension=".bin", initialfile = filename)

    filename_array = (ctypes.c_int*(len(file_path.name) + 1))()
    if (file_path != None):
     for i in range (len(file_path.name)):
       filename_array[i] = int(ord(file_path.name[i]))

     filename_array[i+1] = 0

       
     usgfw2.start_write_RF_to_bin_file(ctypes.pointer(filename_array), len(filename_array), 1)
     usgfw2.get_cine_frame(start.value + Cine_frame_slider.get() - 1)
     usgfw2.stop_write_RF_to_bin_file()
 




def RF_Data_N_frames_button():

    try:
      N = int(RF_Data_N_frames_editbox.get(1.0,END))       
    except ValueError:
      ctypes.windll.user32.MessageBoxW(None, u"Field is empty or enetered value is not number", u"Error", 0)
      return
    else:
      if (int(N)<1 or (int(N)>(end.value-start.value))):
       ctypes.windll.user32.MessageBoxW(None, u"Entered value outside cine loop limits", u"Error", 0)
       return    
    
    PROBE_CODE = usgfw2.get_probe_code()
    PROBE =""
    
    aReg = ConnectRegistry(None, HKEY_LOCAL_MACHINE) 
    aKey = r"SOFTWARE\TELEMED\Usgfw2\Probes"

    aKey = OpenKey(aReg, aKey)
    
    try:
     i = 0
     while True:
         
        asubkey_name = EnumKey(aKey, i)
        i=i+1
        asubkey = OpenKey(aKey, asubkey_name)
        val = QueryValueEx(asubkey, "Device Code")
        if (int(val[0]) == PROBE_CODE):
           PROBE = asubkey_name       
    except WindowsError:
     # WindowsError: [Errno 259] No more data is available    
     pass

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    filename = dt_string[11:13] + '.' + dt_string[14:16] + '.' + dt_string[17:19] + '_' + dt_string[0:2] + '-' + dt_string[3:5] + '-' + dt_string[6:10] +'_' +PROBE +'.bin'
    file_path = filedialog.asksaveasfile(mode='w', defaultextension=".bin", initialfile = filename)

    filename_array = (ctypes.c_int*(len(file_path.name) + 1))()
    if (file_path != None):
     for i in range (len(file_path.name)):
       filename_array[i] = int(ord(file_path.name[i]))

     filename_array[i+1] = 0
     usgfw2.start_write_RF_to_bin_file(ctypes.pointer(filename_array), len(filename_array), 1)

     

     for i in range(0,N): 
        usgfw2.get_cine_frame(i + start.value + Cine_frame_slider.get() - 1)

     usgfw2.stop_write_RF_to_bin_file()

    
def RF_Data_Save_button():
 
    try:
      RF_from = int(RF_Data_From_frames_editbox.get(1.0,END))
      RF_to = int(RF_Data_To_frames_editbox.get(1.0,END))  
    except ValueError:
      ctypes.windll.user32.MessageBoxW(None, u"Field is empty or enetered value is not number", u"Error", 0)
      return
    else:
      if (int(RF_from)<1 or int(RF_to)<1 or (int(RF_to)>(end.value-start.value)) or (int(RF_from)>(end.value-start.value)) or (RF_from>=RF_to)):
       ctypes.windll.user32.MessageBoxW(None, u"Entered value outside cine loop limits", u"Error", 0)
       return    
    
    PROBE_CODE = usgfw2.get_probe_code()
    PROBE =""
    
    aReg = ConnectRegistry(None, HKEY_LOCAL_MACHINE) 
    aKey = r"SOFTWARE\TELEMED\Usgfw2\Probes"

    aKey = OpenKey(aReg, aKey)
    
    try:
     i = 0
     while True:
         
        asubkey_name = EnumKey(aKey, i)
        i=i+1
        asubkey = OpenKey(aKey, asubkey_name)
        val = QueryValueEx(asubkey, "Device Code")
        if (int(val[0]) == PROBE_CODE):
           PROBE = asubkey_name       
    except WindowsError:
     # WindowsError: [Errno 259] No more data is available    
     pass

    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
    filename = dt_string[11:13] + '.' + dt_string[14:16] + '.' + dt_string[17:19] + '_' + dt_string[0:2] + '-' + dt_string[3:5] + '-' + dt_string[6:10] +'_' +PROBE +'.bin'
    file_path = filedialog.asksaveasfile(mode='w', defaultextension=".bin", initialfile = filename)

    filename_array = (ctypes.c_int*(len(file_path.name) + 1))()
    if (file_path != None):
     for i in range (len(file_path.name)):
       filename_array[i] = int(ord(file_path.name[i]))

     filename_array[i+1] = 0
     usgfw2.start_write_RF_to_bin_file(ctypes.pointer(filename_array), len(filename_array), 1)

    for i in range (RF_from, RF_to+1):   
      usgfw2.get_cine_frame((i-1) + start.value)

    usgfw2.stop_write_RF_to_bin_file()

# ----------------------------- Probe button --------------------------------------------------
def on_probe_button_clicked():
    usgfw2.on_probe_button_pressed(0,0,w,h,0,0,0)
    usgfw2.RF_Data_source_ID(source_ID);
    usgfw2.RF_window_set(depth1.value,depth2.value, line1.value,line2.value)
   
    
def clicked_freeze(usgfw2):

    btn1.configure(state = 'disabled')
    btn.configure(state = 'normal')
    global stop_imaging
    stop_imaging = 1;
    usgfw2.Freeze_ultrasound_scanning()

    # ---- Disable controls when freeze -------------------------  
    WideView_angle_button_minus.configure(state = 'disabled')
    WideView_angle_button_plus.configure(state = 'disabled')
    Compound_angle_button_minus.configure(state = 'disabled')
    Compound_angle_button_plus.configure(state = 'disabled')
    Compound_frames_button_minus.configure(state = 'disabled')
    Compound_frames_button_plus.configure(state = 'disabled')
    Compound_subframes_button_minus.configure(state = 'disabled')
    Compound_subframes_button_plus.configure(state = 'disabled') 
    frequency_button_minus.configure(state = 'disabled')
    frequency_button_plus.configure(state = 'disabled')
    depth_button_plus.configure(state = 'disabled')
    depth_button_minus.configure(state = 'disabled')
    gain_slider.configure(state = 'disabled')
    power_slider.configure(state = 'disabled')
    lines_density_button_minus.configure(state = 'disabled')
    lines_density_button_plus.configure(state = 'disabled')
    view_area_button_minus.configure(state = 'disabled')
    view_area_button_plus.configure(state = 'disabled')
    focal_depth_button_minus.configure(state = 'disabled')
    focal_depth_button_plus.configure(state = 'disabled')
    tgc_slider1.configure(state = 'disabled')
    tgc_slider2.configure(state = 'disabled')   
    tgc_slider3.configure(state = 'disabled')
    tgc_slider4.configure(state = 'disabled')
    tgc_slider5.configure(state = 'disabled')
    radiobutton1.configure(state = 'disabled')
    radiobutton2.configure(state = 'disabled')
    radiobutton3.configure(state = 'disabled')
    RF_window_right.configure(state = 'disabled')
    RF_window_left.configure(state = 'disabled')
    RF_window_up.configure(state = 'disabled')
    RF_window_down.configure(state = 'disabled')
    RF_window_size_rght.configure(state = 'disabled')
    RF_window_size_lft.configure(state = 'disabled')
    RF_window_size_upp.configure(state = 'disabled')
    RF_window_size_dwn.configure(state = 'disabled')
    radiobutton_beamformer_output.configure(state = 'disabled')
    radiobutton_TFC_poutput.configure(state = 'disabled')
    radiobutton_apodization_output.configure(state = 'disabled')
    radiobutton_hilbert_output.configure(state = 'disabled')
    if (available_steering_angle == 0):
      steering_angle_button_minus.configure(state = 'disabled')
      steering_angle_button_plus.configure(state = 'disabled')
    dynamic_range_button_minus.configure(state = 'disabled')
    dynamic_range_button_plus.configure(state = 'disabled')
    Scan_direction.configure(state = 'disabled')
    Go_to_frame_button.configure(state = 'normal')
    Go_to_frame_editbox.configure(state = 'normal')
    Cine_frame_slider.configure(state = 'normal')
    Stop_Cine_Loop.configure(state = 'normal')
    Play_Cine_Loop.configure(state = 'normal')

    RF_Data_record_single_frame_button.configure(state = 'normal')
    RF_Data_N_frames_button.configure(state = 'normal')
    RF_Data_N_frames_editbox.configure(state = 'normal')
    RF_Data_From_frames_editbox.configure(state = 'normal')
    RF_Data_To_frames_editbox.configure(state = 'normal')
    RF_Data_Save_button.configure(state = 'normal')
    
    # -------- Cine interval ----------------------------
    global position, start, end
    position = ctypes.c_int64(0);
    start = ctypes.c_int64(0);
    end = ctypes.c_int64(0);
    usgfw2.get_cine_interval(ctypes.pointer(position), ctypes.pointer(start),ctypes.pointer(end));
    Cine_frame_slider.config(from_=1, to=end.value-start.value)
    Cine_frame_slider.set(1)
    Cine_loop_frames_label.config(text = str(1) + '/' + str(end.value-start.value))

def clicked_RUN(usgfw2):

     # ---- Enable controls when run -------------------------  
    WideView_angle_button_minus.configure(state = 'normal')
    WideView_angle_button_plus.configure(state = 'normal')
    Compound_angle_button_minus.configure(state = 'normal')
    Compound_angle_button_plus.configure(state = 'normal')
    Compound_frames_button_minus.configure(state = 'normal')
    Compound_frames_button_plus.configure(state = 'normal')
    Compound_subframes_button_minus.configure(state = 'normal')
    Compound_subframes_button_plus.configure(state = 'normal') 
    frequency_button_minus.configure(state = 'normal')
    frequency_button_plus.configure(state = 'normal')
    depth_button_plus.configure(state = 'normal')
    depth_button_minus.configure(state = 'normal')
    gain_slider.configure(state = 'normal')
    power_slider.configure(state = 'normal')
    lines_density_button_minus.configure(state = 'normal')
    lines_density_button_plus.configure(state = 'normal')
    view_area_button_minus.configure(state = 'normal')
    view_area_button_plus.configure(state = 'normal')
    focal_depth_button_minus.configure(state = 'normal')
    focal_depth_button_plus.configure(state = 'normal')
    tgc_slider1.configure(state = 'normal')
    tgc_slider2.configure(state = 'normal')   
    tgc_slider3.configure(state = 'normal')
    tgc_slider4.configure(state = 'normal')
    tgc_slider5.configure(state = 'normal')
    radiobutton1.configure(state = 'normal')
    radiobutton2.configure(state = 'normal')
    radiobutton3.configure(state = 'normal')
    RF_window_right.configure(state = 'normal')
    RF_window_left.configure(state = 'normal')
    RF_window_up.configure(state = 'normal')
    RF_window_down.configure(state = 'normal')
    RF_window_size_rght.configure(state = 'normal')
    RF_window_size_lft.configure(state = 'normal')
    RF_window_size_upp.configure(state = 'normal')
    RF_window_size_dwn.configure(state = 'normal')
    radiobutton_beamformer_output.configure(state = 'normal')
    radiobutton_TFC_poutput.configure(state = 'normal')
    radiobutton_apodization_output.configure(state = 'normal')
    radiobutton_hilbert_output.configure(state = 'normal')
    if (available_steering_angle == 1):
      steering_angle_button_minus.configure(state = 'normal')
      steering_angle_button_plus.configure(state = 'normal')
    dynamic_range_button_minus.configure(state = 'normal')
    dynamic_range_button_plus.configure(state = 'normal')
    Scan_direction.configure(state = 'normal')

    btn.configure(state = 'disabled')
    btn1.configure(state = 'normal')

    Go_to_frame_button.configure(state = 'disabled')
    Go_to_frame_editbox.configure(state = 'disabled')
    Cine_frame_slider.configure(state = 'disabled')
    Stop_Cine_Loop.configure(state = 'disabled')
    Play_Cine_Loop.configure(state = 'disabled')

    RF_Data_record_single_frame_button.configure(state = 'disabled')
    RF_Data_N_frames_button.configure(state = 'disabled')
    RF_Data_N_frames_editbox.configure(state = 'disabled')
    RF_Data_From_frames_editbox.configure(state = 'disabled')
    RF_Data_To_frames_editbox.configure(state = 'disabled')
    RF_Data_Save_button.configure(state = 'disabled')

    run_loop = 1;
    global focal_depth_marker, buffer_as_numpy_array, RF_line, RFimg, RF_buffer_as_numpy_array, RFimg2, number_of_samples_in_window_for_beam, Q_component_label, ax, difference1,reshaped_array, X_axis, Y_axis, p_array, p1, p2, img, res_X, res_Y, fig, plt1, P1, P2, P3, P4, RF_Row_to_show, RFimg, RFimg2, FPS_label,Q_component_label, RF_window, RF_line
    
    usgfw2.Run_ultrasound_scanning()
    p_array = (ctypes.c_uint*w*h*4)()

    p1 = ctypes.c_int(0); 
    p2 = ctypes.c_float(0.0); 

    
    usgfw2.return_pixel_values2(ctypes.pointer(p_array), ctypes.pointer(p1), ctypes.pointer(p2))
    buffer_as_numpy_array = np.frombuffer(p_array, np.uint)  
    reshaped_array = np.reshape(buffer_as_numpy_array,(w, h, 4))
     
    fig, ax = plt.subplots(1,3, gridspec_kw={'width_ratios':[7.5,1.25,1.25]})
    #fig.tight_layout()
    fig.subplots_adjust(left=0.1, bottom=0.1, right=0.95, top=0.95, wspace=0.25, hspace=None)
    #fig.tight_layout(h_pad=1.42, w_pad=None)

    #fig.set_figheight(5)
    #fig.set_figwidth(8)
    fig.patch.set_facecolor((0.94, 0.94, 0.94))
    ax[0].set_facecolor((0.94, 0.94, 0.94))
    img = ax[0].imshow(reshaped_array[::-1,:,0], cmap="gray",vmin=0, vmax=255,origin='lower',
                 extent =[np.amin(X_axis), np.amax(X_axis), np.amax(Y_axis), np.amin(Y_axis)])
          
    ax[0].set_xlabel('Width [mm]')
    ax[0].set_ylabel('Depth [mm]')
    ax[0].axis('equal')

    # -------------- RF window and RF line drawing -------------------------------------------- 
    rect_position_x_1 = np.zeros(shape=(line2.value - line1.value + 1, 1));
    rect_position_y_1 = np.zeros(shape=(line2.value - line1.value + 1, 1));
    rect_position_x_2 = np.zeros(shape=(line2.value - line1.value + 1, 1));
    rect_position_y_2 = np.zeros(shape=(line2.value - line1.value + 1, 1));
    for i in range (line1.value,line2.value + 1):    
         
      X1pix1line = ctypes.c_float(0.0)
      Y1pix1line = ctypes.c_float(0.0)
      X2pix1line = ctypes.c_float(0.0)
      Y2pix1line = ctypes.c_float(0.0)
    
      usgfw2.convert_units_to_pixels(i,SubFrameIndex.value, depth1.value, depth2.value, ctypes.pointer(X1pix1line), ctypes.pointer(Y1pix1line), ctypes.pointer(X2pix1line), ctypes.pointer(Y2pix1line))

      #X1pix2line = ctypes.c_float(0.0)
      #Y1pix2line = ctypes.c_float(0.0)
      #X2pix2line = ctypes.c_float(0.0)
      #Y2pix2line = ctypes.c_float(0.0)
      #usgfw2.convert_units_to_pixels(line2.value,SubFrameIndex.value, depth1.value, depth2.value, ctypes.pointer(X1pix2line), ctypes.pointer(Y1pix2line), ctypes.pointer(X2pix2line), ctypes.pointer(Y2pix2line))

      rect_position_x_1[i - line1.value] = (X1pix1line.value-difference1)*res_X.value;
      rect_position_y_1[i - line1.value] = (Y1pix1line.value)*res_Y.value;

      rect_position_x_2[i - line1.value] = (X2pix1line.value-difference1)*res_X.value;
      rect_position_y_2[i - line1.value] = (Y2pix1line.value)*res_Y.value;

    rect_position_x = np.concatenate((rect_position_x_1, rect_position_x_2[::-1]), axis=None)
    rect_position_y = np.concatenate((rect_position_y_1, rect_position_y_2[::-1]), axis=None) 
    rect_position_x = np.concatenate((rect_position_x, rect_position_x[0]), axis=None)
    rect_position_y = np.concatenate((rect_position_y, rect_position_y[0]), axis=None) 

    #rect_position_x = [(X1pix1line.value-difference1)*res_X.value, (X1pix2line.value-difference1)*res_X.value, (X2pix2line.value-difference1)*res_X.value, (X2pix1line.value-difference1)*res_X.value, (X1pix1line.value-difference1)*res_X.value];
    #rect_position_y = [(Y1pix1line.value)*res_Y.value, (Y1pix2line.value)*res_Y.value, (Y2pix2line.value)*res_Y.value, (Y2pix1line.value)*res_Y.value, (Y1pix1line.value)*res_Y.value];

    RF_window, = ax[0].plot(rect_position_x,rect_position_y, color='red')

    #RF_Row_to_show = int(np.fix(lines_number.value/2));
    #old_RF_Row_to_show = RF_Row_to_show;

    X1pixRFline = ctypes.c_float(0.0)
    Y1pixRFline = ctypes.c_float(0.0)
    X2pixRFline = ctypes.c_float(0.0)
    Y2pixRFline = ctypes.c_float(0.0)
    Line = int(RF_Row_to_show + line1.value) 
    usgfw2.convert_units_to_pixels(Line,SubFrameIndex.value, depth1.value, depth2.value, ctypes.pointer(X1pixRFline), ctypes.pointer(Y1pixRFline), ctypes.pointer(X2pixRFline), ctypes.pointer(Y2pixRFline))

    XRFline = [(X1pixRFline.value-difference1)*res_X.value, (X2pixRFline.value-difference1)*res_Y.value];
    YRFline = [Y1pixRFline.value*res_X.value, Y2pixRFline.value*res_Y.value];
    RF_line, = ax[0].plot(XRFline,YRFline,'g--');

    I_component_label = Label(window, text = "I",fg="blue", font = 14)
    I_component_label.place(x = 487, y = 30) 

    Q_component_label = Label(window, text = "",fg="red", font = 14)
    Q_component_label.place(x = 581, y = 30) 


    focal_depth_marker, = ax[0].plot([np.amin(X_axis), np.amin(X_axis)+1],[focal_depth.value, focal_depth.value],'y')


    # -----------------------------------------------------------------------------   
    P1 = ctypes.c_int(0)  
    P2 = ctypes.c_double(0);     
    P3 = ctypes.c_int(0);      
    P4 = ctypes.c_int(0);       

    if (source_ID == 4):
       p_array_RF = (ctypes.c_int16*number_of_samples_in_window_for_beam*lines_number.value*2)() 
       usgfw2.return_RF_data(ctypes.pointer(p_array_RF),number_of_samples_in_window_for_beam*lines_number.value*2,ctypes.pointer(P1),ctypes.pointer(P2),ctypes.pointer(P3),ctypes.pointer(P4))
    else:
       p_array_RF = (ctypes.c_int16*number_of_samples_in_window_for_beam*lines_number.value)() 
       usgfw2.return_RF_data(ctypes.pointer(p_array_RF),number_of_samples_in_window_for_beam*lines_number.value,ctypes.pointer(P1),ctypes.pointer(P2),ctypes.pointer(P3),ctypes.pointer(P4))

    RF_buffer_as_numpy_array = np.frombuffer(p_array_RF, np.int16)

    RF_data_to_show = RF_buffer_as_numpy_array[RF_Row_to_show*number_of_samples_in_window_for_beam+3:RF_Row_to_show*number_of_samples_in_window_for_beam + number_of_samples_in_window_for_beam]


    y_axis_RF = range(1, number_of_samples_in_window_for_beam-2)
    RFimg, = ax[1].plot(RF_data_to_show, y_axis_RF,color = 'blue',linewidth=0.25)
    ax[1].invert_yaxis()
    ax[1].axis(xmin=-50, xmax = 50, ymin = number_of_samples_in_window_for_beam-1,ymax = 1)
    ax[1].tick_params(axis='both', which='major', labelsize=8, rotation=90)
    ax[1].set_facecolor((0.94, 0.94, 0.94))
 
    ax[2].tick_params(axis='both', which='major', labelsize=8, rotation=90)
    ax[2].set_facecolor((0.94, 0.94, 0.94))
    ax[2].axis('off')
 
    #plt2.figure("2")
    #plt2.plot(RF_data_to_show)
    #plt2.show()

    RFimg2, = ax[2].plot(0,0,color = 'red',linewidth=0.25)
    if (source_ID == 4):
      RF_data_to_show2 = RF_buffer_as_numpy_array[(number_of_samples_in_window_for_beam*lines_number.value) + (RF_Row_to_show*number_of_samples_in_window_for_beam+3):(number_of_samples_in_window_for_beam*lines_number.value)+RF_Row_to_show*number_of_samples_in_window_for_beam + number_of_samples_in_window_for_beam]
      ax[2].axis('on')
      RFimg2, = ax[2].plot(RF_data_to_show2, y_axis_RF,color = 'red',linewidth=0.25)
      Q_component_label.config(text = "Q")



    FPS_label = ttk.Label(window, text = 'FPS =')
    FPS_label.place(x = 200, y = 20)

    usgfw2.RF_window_get(ctypes.pointer(depth1),ctypes.pointer(depth2),ctypes.pointer(line1),ctypes.pointer(line2),ctypes.pointer(lines_number))

    old_depth1 = depth1.value;
    old_depth2 =depth2.value;
    old_line1 = line1.value;
    old_line2 = line2.value;

    
   
    matplotlib.pyplot.close()
    global plt1
    plt1 = FigureCanvasTkAgg(fig,window)
      
    
    while (run_loop==1):

     global stop_imaging    
     if (stop_imaging == 1):
       stop_imaging = 0;
       break;
 
     matplotCanvas(window,ax, difference1,reshaped_array[:,:,0:3], X_axis, Y_axis, p_array, p1, p2, img, usgfw2, res_X, res_Y, fig, plt1, P1, P2, P3, P4, RF_Row_to_show, RFimg, RFimg2, FPS_label,Q_component_label, RF_window, RF_line, focal_depth_marker)


    
 
window.config(menu=menu)

def matplotCanvas(window,ax, difference1,reshaped,X_axis, Y_axis, p_array, p1, p2, img, usgfw2, res_X, res_Y, f, plt1, P1, P2, P3, P4, RF_Row_to_show, RFimg, RFimg2, FPS_label, Q_component_label, RF_window, RF_line, focal_depth_marker):
      
     start_time = time.time()  
     #plt = FigureCanvasTkAgg(f,window)

     window.update()

     global RF_buffer_as_numpy_array 
     if (stop_imaging == 1):
        return

     
     usgfw2.RF_window_get(ctypes.pointer(depth1), ctypes.pointer(depth2), ctypes.pointer(line1), ctypes.pointer(line2), ctypes.pointer(lines_number))
     usgfw2.get_resolution(ctypes.pointer(res_X),ctypes.pointer(res_Y))

     RF_line_slider.config(from_=0, to=lines_number.value-1)
     RF_line_slider_label.config(text = str(RF_Row_to_show+1)+ '/' + str(lines_number.value))

     if (RF_Row_to_show+1 > lines_number.value and (lines_number.value-RF_Row_to_show+1)!=0):
         RF_Row_to_show = int((lines_number.value-1)/2)
         RF_line_slider.set(RF_Row_to_show)
     if ((lines_number.value-RF_Row_to_show+1)==0):
         RF_Row_to_show = lines_number.value-1
         RF_line_slider.set(RF_Row_to_show)
    
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
          Y_axis[i] = i*res_Y.value - Y1pix1line_0.value*res_Y.value;

      

     #X1pix1line = ctypes.c_float(0.0)
     #Y1pix1line = ctypes.c_float(0.0)
     #X2pix1line = ctypes.c_float(0.0)
     #Y2pix1line = ctypes.c_float(0.0)
    
     #X1pix2line = ctypes.c_float(0.0)
     #Y1pix2line = ctypes.c_float(0.0)
     #X2pix2line = ctypes.c_float(0.0)
     #Y2pix2line = ctypes.c_float(0.0)
      
     #usgfw2.convert_units_to_pixels(line1.value, SubFrameIndex.value,depth1.value, depth2.value, ctypes.pointer(X1pix1line), ctypes.pointer(Y1pix1line), ctypes.pointer(X2pix1line), ctypes.pointer(Y2pix1line))
     #usgfw2.convert_units_to_pixels(line2.value, SubFrameIndex.value,depth1.value, depth2.value, ctypes.pointer(X1pix2line), ctypes.pointer(Y1pix2line), ctypes.pointer(X2pix2line), ctypes.pointer(Y2pix2line))

     #rect_position_x = [(X1pix1line.value-difference1)*res_X.value, (X1pix2line.value-difference1)*res_X.value, (X2pix2line.value-difference1)*res_X.value, (X2pix1line.value-difference1)*res_X.value, (X1pix1line.value-difference1)*res_X.value];
     #rect_position_y = [(Y1pix1line.value)*res_Y.value, (Y1pix2line.value)*res_Y.value, (Y2pix2line.value)*res_Y.value, (Y2pix1line.value)*res_Y.value, (Y1pix1line.value)*res_Y.value];

     rect_position_x_1 = np.zeros(shape=(line2.value - line1.value + 1, 1));
     rect_position_y_1 = np.zeros(shape=(line2.value - line1.value + 1, 1));
     rect_position_x_2 = np.zeros(shape=(line2.value - line1.value + 1, 1));
     rect_position_y_2 = np.zeros(shape=(line2.value - line1.value + 1, 1)); 
     for i in range (line1.value,line2.value + 1):    
         
      X1pix1line = ctypes.c_float(0.0)
      Y1pix1line = ctypes.c_float(0.0)
      X2pix1line = ctypes.c_float(0.0)
      Y2pix1line = ctypes.c_float(0.0)
    
      usgfw2.convert_units_to_pixels(i,SubFrameIndex.value, depth1.value, depth2.value, ctypes.pointer(X1pix1line), ctypes.pointer(Y1pix1line), ctypes.pointer(X2pix1line), ctypes.pointer(Y2pix1line))

      #X1pix2line = ctypes.c_float(0.0)
      #Y1pix2line = ctypes.c_float(0.0)
      #X2pix2line = ctypes.c_float(0.0)
      #Y2pix2line = ctypes.c_float(0.0)
      #usgfw2.convert_units_to_pixels(line2.value,SubFrameIndex.value, depth1.value, depth2.value, ctypes.pointer(X1pix2line), ctypes.pointer(Y1pix2line), ctypes.pointer(X2pix2line), ctypes.pointer(Y2pix2line))

      rect_position_x_1[i - line1.value] = (X1pix1line.value-difference1)*res_X.value;
      rect_position_y_1[i - line1.value] = (Y1pix1line.value)*res_Y.value;

      rect_position_x_2[i - line1.value] = (X2pix1line.value-difference1)*res_X.value;
      rect_position_y_2[i - line1.value] = (Y2pix1line.value)*res_Y.value;

     rect_position_x = np.concatenate((rect_position_x_1, rect_position_x_2[::-1]), axis=None)
     rect_position_y = np.concatenate((rect_position_y_1, rect_position_y_2[::-1]), axis=None) 
     rect_position_x = np.concatenate((rect_position_x, rect_position_x[0]), axis=None)
     rect_position_y = np.concatenate((rect_position_y, rect_position_y[0]), axis=None) 

     RF_window.set_xdata(rect_position_x);
     RF_window.set_ydata(rect_position_y - Y1pix1line_0.value*res_Y.value);

     X1pixRFline = ctypes.c_float(0.0)
     Y1pixRFline = ctypes.c_float(0.0)
     X2pixRFline = ctypes.c_float(0.0)
     Y2pixRFline = ctypes.c_float(0.0)
     Line = int(RF_Row_to_show + line1.value) 
     usgfw2.convert_units_to_pixels(Line,SubFrameIndex.value, depth1.value, depth2.value, ctypes.pointer(X1pixRFline), ctypes.pointer(Y1pixRFline), ctypes.pointer(X2pixRFline), ctypes.pointer(Y2pixRFline))

     XRFline = [(X1pixRFline.value-difference1)*res_X.value, (X2pixRFline.value-difference1)*res_Y.value];
     YRFline = [Y1pixRFline.value*res_X.value - Y1pix1line_0.value*res_Y.value, Y2pixRFline.value*res_Y.value - Y1pix1line_0.value*res_Y.value];

     RF_line.set_xdata(XRFline);
     RF_line.set_ydata(YRFline); 

     focal_depth_marker.set_xdata([np.amin(X_axis), np.amin(X_axis)+1]);
     focal_depth_marker.set_ydata([focal_depth.value, focal_depth.value]);


     usgfw2.return_pixel_values2(ctypes.pointer(p_array), ctypes.pointer(p1), ctypes.pointer(p2))
     buffer_as_numpy_array = np.frombuffer(p_array, np.uint)  
     reshaped_array = np.reshape(buffer_as_numpy_array,(w, h, 4))
    
     img.set_data(reshaped_array[::-1,:,0])
     img.set_extent([np.amin(X_axis), np.amax(X_axis), np.amax(Y_axis), np.amin(Y_axis)])

     #plt1.get_tk_widget().pack()
     #plt1.place(x = 30, y = 50)

     # ---------- RF imaging ------------------------------------------------------------------
     number_of_samples_in_window_for_beam = int(numpy.fix(2*((depth2.value-depth1.value)/1000)/1540/((sampling_period_ns.value)*1e-9)))
     if (source_ID == 4):
       p_array_RF = (ctypes.c_int16*number_of_samples_in_window_for_beam*lines_number.value*2)() 
       usgfw2.return_RF_data(ctypes.pointer(p_array_RF),number_of_samples_in_window_for_beam*lines_number.value*2,ctypes.pointer(P1),ctypes.pointer(P2),ctypes.pointer(P3),ctypes.pointer(P4))
       ax[2].axis('on')
     else:
       p_array_RF = (ctypes.c_int16*number_of_samples_in_window_for_beam*lines_number.value)() 
       usgfw2.return_RF_data(ctypes.pointer(p_array_RF),number_of_samples_in_window_for_beam*lines_number.value,ctypes.pointer(P1),ctypes.pointer(P2),ctypes.pointer(P3),ctypes.pointer(P4))
       ax[2].axis('off')
 

     RF_buffer_as_numpy_array = np.frombuffer(p_array_RF, np.int16)
    
     RF_data_to_show = RF_buffer_as_numpy_array[RF_Row_to_show*number_of_samples_in_window_for_beam+3:RF_Row_to_show*number_of_samples_in_window_for_beam + number_of_samples_in_window_for_beam]
     y_axis_RF = range(1, number_of_samples_in_window_for_beam-2)
     
     if (source_ID == 4):
      RF_data_to_show2 = RF_buffer_as_numpy_array[(number_of_samples_in_window_for_beam*lines_number.value) + (RF_Row_to_show*number_of_samples_in_window_for_beam+3):(number_of_samples_in_window_for_beam*lines_number.value)+RF_Row_to_show*number_of_samples_in_window_for_beam + number_of_samples_in_window_for_beam]
      RFimg2.set_xdata(RF_data_to_show2)
      RFimg2.set_ydata(y_axis_RF)
      if (AutoSC == 1):
       ax[2].axis(xmin=np.amin(RF_data_to_show2)-5, xmax = np.amax(RF_data_to_show2)+5, ymin = number_of_samples_in_window_for_beam-1,ymax = 1) 
      else:
       ax[2].axis(xmin=-2**bits/2, xmax = 2**bits/2, ymin = number_of_samples_in_window_for_beam-1,ymax = 1)
      Q_component_label.config(text = "Q")
     else:
      RFimg2.set_xdata(0)
      RFimg2.set_ydata(0)
      Q_component_label.config(text = "   ")
           
     RFimg.set_xdata(RF_data_to_show)
     RFimg.set_ydata(y_axis_RF)
     if (AutoSC == 1):
       ax[1].axis(xmin=np.amin(RF_data_to_show)-5, xmax = np.amax(RF_data_to_show)+5, ymin = number_of_samples_in_window_for_beam-1,ymax = 1) 
     else:
       ax[1].axis(xmin=-2**bits/2, xmax = 2**bits/2, ymin = number_of_samples_in_window_for_beam-1,ymax = 1)
     
        
     plt1.draw()
     #pause(1/120)


     # plt1.get_tk_widget().grid(row=50,column=50)
     plt1.get_tk_widget().place(x=10,y=50)

    
     FPS_label.configure(text = 'FPS = ' + str(round(1/(time.time() - start_time))))
          
     #canvas.draw()
     #toolbar_frame = Frame(window)
     #toolbar_frame.grid(row=21,column=6,columnspan=2)
     #toolbar = NavigationToolbar2Tk( plt1, toolbar_frame )

      

# ----------------- Ultrasonography controls --------------------------------------------------
btn = Button(window, text="Run", command=lambda:clicked_RUN(usgfw2), height = 1, width = 8)
btn.place(x=20, y=20)

btn1 = Button(window, text="Freeze", command=lambda:clicked_freeze(usgfw2), height = 1, width = 8)
btn1.place(x=90, y=20)

# ----------------- B mode controls --------------------------------------------------
frequency_button_minus = Button(tab1, text="<", command=lambda:frequency_button_down(usgfw2, frequency_label), height = 1, width = 8)
frequency_button_minus.place(x=20, y=25)

frequency_button_plus = Button(tab1, text=">", command=lambda:frequency_button_up(usgfw2, frequency_label), height = 1, width = 8)
frequency_button_plus.place(x=90, y=25)

depth_button_minus = Button(tab1, text="<", command=lambda:depth_button_down(usgfw2, depth_label), height = 1, width = 8)
depth_button_minus.place(x=20, y=75)

depth_button_plus = Button(tab1, text=">", command=lambda:depth_button_up(usgfw2, depth_label), height = 1, width = 8)
depth_button_plus.place(x=90, y=75)

gain_slider = Scale(tab1, from_=0, to=90, orient=HORIZONTAL,command=gain_slider_click,showvalue = 0, length = 135)
gain_slider.set(70)
gain_slider.place(x=20, y=120)

power_slider = Scale(tab1, from_=0, to=20, orient=HORIZONTAL,command=power_slider_click,showvalue = 0, length = 135)
power_slider.set(20)
power_slider.place(x=20, y=160)

lines_density_button_minus = Button(tab1, text="<", command=lambda:lines_density_button_down(usgfw2, lines_density_label), height = 1, width = 8)
lines_density_button_minus.place(x=20, y=200)

lines_density_button_plus = Button(tab1, text=">", command=lambda:lines_density_button_up(usgfw2, lines_density_label), height = 1, width = 8)
lines_density_button_plus.place(x=90, y=200)

view_area_button_minus = Button(tab1, text="<", command=lambda:view_area_button_down(usgfw2, view_area_label), height = 1, width = 8)
view_area_button_minus.place(x=20, y=250)

view_area_button_plus = Button(tab1, text=">", command=lambda:view_area_button_up(usgfw2, view_area_label), height = 1, width = 8)
view_area_button_plus.place(x=90, y=250)


focal_depth_button_minus = Button(tab1, text="<", command=lambda:focal_depth_button_down(usgfw2, focal_depth_label), height = 1, width = 8)
focal_depth_button_minus.place(x=20, y=300)

focal_depth_button_plus = Button(tab1, text=">", command=lambda:focal_depth_button_up(usgfw2, focal_depth_label), height = 1, width = 8)
focal_depth_button_plus.place(x=90, y=300)

steering_angle_button_minus = Button(tab1, text="<", command=lambda:steering_angle_button_down(usgfw2, steering_angle_label), height = 1, width = 8)
steering_angle_button_minus.place(x=20, y=350)

steering_angle_button_plus = Button(tab1, text=">", command=lambda:steering_angle_button_up(usgfw2, steering_angle_label), height = 1, width = 8)
steering_angle_button_plus.place(x=90, y=350)

available_steering_angle = usgfw2.steering_angle()
if (available_steering_angle == 0):    
    steering_angle_button_minus.configure(state = 'disabled')
    steering_angle_button_plus.configure(state = 'disabled')
else:
    steering_angle_button_minus.configure(state = 'normal')
    steering_angle_button_plus.configure(state = 'normal')
    

dynamic_range_button_minus = Button(tab1, text="<", command=lambda:dynamic_range_button_down(usgfw2, dynamic_range_label), height = 1, width = 8)
dynamic_range_button_minus.place(x=20, y=400)

dynamic_range_button_plus = Button(tab1, text=">", command=lambda:dynamic_range_button_up(usgfw2, dynamic_range_label), height = 1, width = 8)
dynamic_range_button_plus.place(x=90, y=400)

Scan_direction = Checkbutton(tab1, text='Change Scan Direction', variable=var1,onvalue=1, offvalue=0, command=change_scan_dir)
Scan_direction.place(x=20, y=430)

tgc_slider1 = Scale(tab1, from_=0, to=100, orient=HORIZONTAL,command=tgc1_slider_click,showvalue = 0, length = 135)
tgc_slider1.set(50)
tgc_slider1.place(x=250, y=270)

tgc_slider2 = Scale(tab1, from_=0, to=100, orient=HORIZONTAL,command=tgc2_slider_click,showvalue = 0, length = 135)
tgc_slider2.set(60)
tgc_slider2.place(x=250, y=300)

tgc_slider3 = Scale(tab1, from_=0, to=100, orient=HORIZONTAL,command=tgc3_slider_click,showvalue = 0, length = 135)
tgc_slider3.set(60)
tgc_slider3.place(x=250, y=330)

tgc_slider4 = Scale(tab1, from_=0, to=100, orient=HORIZONTAL,command=tgc4_slider_click,showvalue = 0, length = 135)
tgc_slider4.set(60)
tgc_slider4.place(x=250, y=360)

tgc_slider5 = Scale(tab1, from_=0, to=100, orient=HORIZONTAL,command=tgc5_slider_click, showvalue = 0, length = 135)
tgc_slider5.set(60)
tgc_slider5.place(x=250, y=390)

radiobutton1 = Radiobutton(tab1, text = 'B Standard', command = lambda:radiobutton1_clicked(usgfw2, lines_density_label), variable=r1_v, state='active', value = 1)
radiobutton1.place(x=240, y=20)
r1_v.set(1)

radiobutton2 = Radiobutton(tab1, text = 'B WideView', command = lambda:radiobutton2_clicked(usgfw2, lines_density_label), variable=r2_v)
radiobutton2.place(x=240, y=60)
r2_v.set(0)
   
radiobutton3 = Radiobutton(tab1, text = 'B Compound', command = lambda:radiobutton3_clicked(usgfw2, lines_density_label), variable=r3_v)
radiobutton3.place(x=240, y=105)
r3_v.set(0)

WideView_angle_button_minus = Button(tab1, text="<", command=lambda:WideView_angle_button_down(usgfw2, WideView_angle_label), height = 1, width = 8)
WideView_angle_button_minus.place(x=340, y=60)

WideView_angle_button_plus = Button(tab1, text=">", command=lambda:WideView_angle_button_up(usgfw2, WideView_angle_label), height = 1, width = 8)
WideView_angle_button_plus.place(x=410, y=60)

Compound_angle_button_minus = Button(tab1, text="<", command=lambda:Compound_angle_button_down(usgfw2, Compound_angle_label), height = 1, width = 8)
Compound_angle_button_minus.place(x=340, y=110)

Compound_angle_button_plus = Button(tab1, text=">", command=lambda:Compound_angle_button_up(usgfw2, Compound_angle_label), height = 1, width = 8)
Compound_angle_button_plus.place(x=410, y=110)

Compound_frames_button_minus = Button(tab1, text="<", command=lambda:Compound_frames_button_down(usgfw2, Compound_frames_label, Compound_subframes_label), height = 1, width = 8)
Compound_frames_button_minus.place(x=340, y=160)

Compound_frames_button_plus = Button(tab1, text=">", command=lambda:Compound_frames_button_up(usgfw2, Compound_frames_label, Compound_subframes_label), height = 1, width = 8)
Compound_frames_button_plus.place(x=410, y=160)

Compound_subframes_button_minus = Button(tab1, text="<", command=lambda:Compound_subframes_button_down(usgfw2, Compound_subframes_label), height = 1, width = 8)
Compound_subframes_button_minus.place(x=340, y=210)

Compound_subframes_button_plus = Button(tab1, text=">", command=lambda:Compound_subframes_button_up(usgfw2, Compound_subframes_label), height = 1, width = 8)
Compound_subframes_button_plus.place(x=410, y=210)

WideView_angle_button_minus.configure(state = 'disabled')
WideView_angle_button_plus.configure(state = 'disabled')
Compound_angle_button_minus.configure(state = 'disabled')
Compound_angle_button_plus.configure(state = 'disabled')
Compound_frames_button_minus.configure(state = 'disabled')
Compound_frames_button_plus.configure(state = 'disabled')
Compound_subframes_button_minus.configure(state = 'disabled')
Compound_subframes_button_plus.configure(state = 'disabled') 

# ----------------- RF controls --------------------------------------------------
RF_window_move_label = ttk.Label(tab2, text = "RF Window Position:")
RF_window_move_label.place(x = 20, y = 120)
RF_window_right = Button(tab2, text=">", command=lambda:RF_window_move_right(usgfw2), height = 2, width = 5)
RF_window_right.place(x=105, y=180)
RF_window_left = Button(tab2, text="<", command=lambda:RF_window_move_left(usgfw2), height = 2, width = 5)
RF_window_left.place(x=20, y=180)
RF_window_up = Button(tab2, text="^", command=lambda:RF_window_move_up(usgfw2), height = 2, width = 5)
RF_window_up.place(x=63, y=140)
RF_window_down = Button(tab2, text="v", command=lambda:RF_window_move_down(usgfw2), height = 2, width = 5)
RF_window_down.place(x=63, y=220)

RF_window_size_label = ttk.Label(tab2, text = "RF Window Size:")
RF_window_size_label.place(x = 220, y = 120)
RF_window_size_rght = Button(tab2, text=">", command=lambda:RF_window_size_right(usgfw2), height = 2, width = 5)
RF_window_size_rght.place(x=305, y=180)
RF_window_size_lft = Button(tab2, text="<", command=lambda:RF_window_size_left(usgfw2), height = 2, width = 5)
RF_window_size_lft.place(x=220, y=180)
RF_window_size_upp = Button(tab2, text="^", command=lambda:RF_window_size_up(usgfw2), height = 2, width = 5)
RF_window_size_upp.place(x=263, y=140)
RF_window_size_dwn = Button(tab2, text="v", command=lambda:RF_window_size_down(usgfw2), height = 2, width = 5)
RF_window_size_dwn.place(x=263, y=220)


RF_line_slider = Scale(tab2, from_=0, to=lines_number.value-1, orient=HORIZONTAL,command=RF_line_slider_click,showvalue = 0, length = 135)
RF_line_slider.set(int(np.fix((line2.value-line1.value)/2)))
RF_line_slider.place(x=20, y=300)

RF_line_slider_name_label = Label(tab2, text = "RF Line:")
RF_line_slider_name_label.place(x=20, y=280)

RF_line_slider_label = Label(tab2, text = str(int(np.fix((line2.value-line1.value)/2)))+ '/' + str(lines_number.value))
RF_line_slider_label.place(x=180, y=300)

radiobutton_beamformer_output = Radiobutton(tab2, text = 'Beamformer output (I, 16 bit)', command = lambda:radiobutton_beamformer_output_clicked(usgfw2), variable=r4_v, state='active', value = 1)
radiobutton_beamformer_output.place(x=20, y=25)
r4_v.set(1)

radiobutton_TFC_poutput = Radiobutton(tab2, text = 'TFC filter output (I, 16 bit)', command = lambda:radiobutton_TFC_poutput_clicked(usgfw2), variable=r5_v)
radiobutton_TFC_poutput.place(x=20, y=45)
r5_v.set(0)

radiobutton_apodization_output = Radiobutton(tab2, text = 'Angle apodization output (I, 16 bit)', command = lambda:radiobutton_apodization_output_clicked(usgfw2), variable=r6_v)
radiobutton_apodization_output.place(x=20, y=65)
r6_v.set(0)

radiobutton_hilbert_output = Radiobutton(tab2, text = 'Hilbert transform output (I + Q, 16 bit + 16 bit)', command = lambda:radiobutton_hilbert_output_clicked(usgfw2), variable=r7_v)
radiobutton_hilbert_output.place(x=20, y=85)
r7_v.set(0)

RF_data_source_label = Label(tab2, text = 'RF Data Source Point:')
RF_data_source_label.place(x = 20, y = 5)

IQ_autofit = Checkbutton(window, text='I, Q autofit', variable=var2, onvalue=1, offvalue=0, command = Autoscale)
IQ_autofit.place(x=487, y=530)

IQ_bits_rigth = Button(window, text=">", command=IQ_bits_up, height = 1, width = 5)
IQ_bits_rigth.place(x=532, y=555)
IQ_bits_left = Button(window, text="<", command=IQ_bits_down, height = 1, width = 5)
IQ_bits_left.place(x=487, y=555)

# ----------------- Cine controls --------------------------------------------------
Cine_loop_label = Label(tab3, text = 'Cine control:')
Cine_loop_label.place(x = 20, y = 5)

Play_Cine_Loop = Button(tab3, text="Play", command=Play_cine, height = 1, width = 15)
Play_Cine_Loop.place(x=20, y=30)

Stop_Cine_Loop = Button(tab3, text="Stop", command=Stop_cine, height = 1, width = 15)
Stop_Cine_Loop.place(x=145, y=30)

Cine_frame_slider = Scale(tab3, from_=1, to=100, orient=HORIZONTAL, showvalue = 0, length = 240)
Cine_frame_slider.set(1)
Cine_frame_slider.place(x=20, y=70)

Cine_frame_slider.bind("<ButtonRelease-1>", Cine_frame_slider_click)

Cine_loop_frames_label = Label(tab3)
Cine_loop_frames_label.place(x = 265, y = 70)

Go_to_cine_frame_label = Label(tab3, text = "Go to frame:")
Go_to_cine_frame_label.place(x = 20, y = 95)

Go_to_frame_editbox = Text(tab3, height = 1, width = 4)
Go_to_frame_editbox.place(x = 95, y = 95)

Go_to_frame_button = Button(tab3, text="Apply", command=Go_to_frame_button_click, height = 1, width = 5)
Go_to_frame_button.place(x = 140, y = 94)

# ----------------- RF data recording controls --------------------------------------------------
RF_Data_record_label = Label(tab3, text = "RF Data Record:")
RF_Data_record_label.place(x = 20, y = 140)

RF_Data_record_single_frame_button = Button(tab3, text="Record Single Frame", command=RF_Data_record_single_frame_button_click, height = 1, width = 17)
RF_Data_record_single_frame_button.place(x = 20, y = 165)

RF_Data_N_frames_button = Button(tab3, text="Record N Frames", command=RF_Data_N_frames_button, height = 1, width = 17)
RF_Data_N_frames_button.place(x = 20, y = 200)

RF_Data_N_frames_label = Label(tab3, text = "N:")
RF_Data_N_frames_label.place(x = 155, y = 200)

RF_Data_N_frames_editbox = Text(tab3, height = 1, width = 4)
RF_Data_N_frames_editbox.place(x = 172, y = 202)

RF_Data_From_frames_label = Label(tab3, text = "From:")
RF_Data_From_frames_label.place(x = 20, y = 230)

RF_Data_From_frames_editbox = Text(tab3, height = 1, width = 4)
RF_Data_From_frames_editbox.place(x = 60, y = 232)

RF_Data_To_frames_label = Label(tab3, text = "To:")
RF_Data_To_frames_label.place(x = 100, y = 230)

RF_Data_To_frames_editbox = Text(tab3, height = 1, width = 4)
RF_Data_To_frames_editbox.place(x = 130, y = 232)

RF_Data_Save_button = Button(tab3, text="Save", command=RF_Data_Save_button, height = 1, width = 8)
RF_Data_Save_button.place(x = 180, y = 230)

# --------------Settings buttons -----------------------------------------------------------------
On_probe_button = Button(tab4, text="Probe", command=on_probe_button_clicked, height = 1, width = 8)
On_probe_button.place(x = 20, y = 20)

# --------------Add Logo-----------------------------------------------------------------
LOGO_label = Label(tab1, image = img_logo)
LOGO_label.place(x = 360, y = 430)
PC_ultrasound = Label(tab1, text = "www.pcultrasound.com")
PC_ultrasound.place(x = 390, y = 495)

# -------------------------------------------------------------------------------------------------
 
btn.invoke()        
window.mainloop()







