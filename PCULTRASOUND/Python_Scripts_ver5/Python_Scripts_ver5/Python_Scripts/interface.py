import tkinter
from tkinter import *
from tkinter import filedialog
from tkinter import Menu

import struct
import os
import math
import scipy
import numpy
import matplotlib 

matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

window = Tk()
window.title("Python RF data viewer v1.0")
window.geometry('850x700')

menu = Menu(window)
new_item = Menu(menu)

def clicked3():
 global filename
 filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("bin files","*.bin"),("all files","*.*")))

 statinfo = os.stat(filename)
 f = open(filename,"rb")

 size_in_bytes_global=0
 stop = 1;

 global i
 i=0;
  
 global RF_data_arr
 global RF_data_arrQ
 global Number_of_RF_rows 
 global tx_frequency 
 global frame_rate 
 global Length_of_RF_row 
 global Sampling_period_ns 
 global BIT_ADC 
 global start_depth 
 global angle 
 global beam_x
 global beam_y
 global size_of_frame
 global source_ID
 global reshapedQ
 
 RF_data_arr = {}
 RF_data_arrQ = {}
 Number_of_RF_rows = {}
 number_of_frames = {}
 header_size = {}
 frame_size = {}
 source_ID = {}
 tx_frequency = {}
 frame_rate = {}
 Length_of_RF_row = {}
 Sampling_period_ns = {}
 BIT_ADC = {}
 start_depth = {}
 angle = {}
 beam_x = {}
 beam_y = {}
 time_staps = {}

# read RF data file
 bytes_to_read = f.read(1 * 6)
 file_type = struct.unpack("6c", bytes_to_read)
 compare_toRF001 = (b'R', b'F', b'0', b'0', b'0', b'1')
 compare_toRF002 = (b'R', b'F', b'0', b'0', b'0', b'2')
 compare_toRF003 = (b'R', b'F', b'0', b'0', b'0', b'3')
 compare_toRF004 = (b'R', b'F', b'0', b'0', b'0', b'4')


 if (file_type==compare_toRF003 or file_type==compare_toRF004):
# read RF data file

  while stop==1:

   bytes_to_read = f.read(11 * 4)
   array = struct.unpack("11i", bytes_to_read)
   array = list(array)

   number_of_frames = array[0]
   header_size = array[1]
   frame_size = array[2]
   source_ID = array[3]
   tx_frequency[i] = array[4]
   frame_rate[i] = float(array[5])/100
   Length_of_RF_row[i] = array[6]
   Number_of_RF_rows[i]=array[7]
   Sampling_period_ns[i]=array[8]
   BIT_ADC[i] = array[9]
   start_depth[i] = array[10]
   size_of_frame = Number_of_RF_rows[i]*Length_of_RF_row[i]
     
   bytes_to_read = f.read(3*Number_of_RF_rows[i] * 4)
   array = struct.unpack("="+str(3*Number_of_RF_rows[i])+"i", bytes_to_read)
   array = list(array)

   angle[i] = array[2::3]
   beam_x[i] =array[0::3]
   beam_y[i] =array[1::3]

   for j in range(Number_of_RF_rows[i]):
       angle[i][j] = float(angle[i][j])/1000000
       beam_x[i][j] = float(beam_x[i][j])/10000+(float(start_depth[i])/10*math.sin(angle[i][j]))
       beam_y[i][j] = float(beam_y[i][j])/10000+(float(start_depth[i])/10*math.cos(angle[i][j]))

   bytes_to_read = f.read(Number_of_RF_rows[i] * 4)
   array = struct.unpack("="+str(Number_of_RF_rows[i])+"i", bytes_to_read)
   array = list(array)
 
   time_stamps = array
 
   if (source_ID != 4):
    bytes_to_read = f.read(size_of_frame * 2)
    array = struct.unpack("="+str(size_of_frame)+"h", bytes_to_read)
    array = list(array)

    RF_data_arr[i]=array

   else:
    bytes_to_read = f.read(size_of_frame * 2)
    array = struct.unpack("="+str(size_of_frame)+"h", bytes_to_read)
    array = list(array)

    RF_data_arr[i]=array

    bytes_to_read = f.read(size_of_frame * 2)
    array = struct.unpack("="+str(size_of_frame)+"h", bytes_to_read)
    array = list(array)

    RF_data_arrQ[i]=array
    size_of_frame = size_of_frame*2

   size_in_bytes_run=(11*4)+(3*Number_of_RF_rows[i]*4)+(size_of_frame*2)+(4*Number_of_RF_rows[i])
   size_in_bytes_global=size_in_bytes_global+size_in_bytes_run
   i=i+1;

   if ((statinfo.st_size-size_in_bytes_global)>=size_in_bytes_run):
      stop = 1
   else:
      stop = 0

 if (file_type==compare_toRF002):
# read RF data file

  while stop==1:

   bytes_to_read = f.read(11 * 4)
   array = struct.unpack("11i", bytes_to_read)
   array = list(array)

   number_of_frames = array[0]
   header_size = array[1]
   frame_size = array[2]
   source_ID = array[3]
   tx_frequency[i] = array[4]
   frame_rate[i] = float(array[5])/100
   Length_of_RF_row[i] = array[6]
   Number_of_RF_rows[i]=array[7]
   Sampling_period_ns[i]=array[8]
   BIT_ADC[i] = array[9]
   start_depth[i] = array[10]
   size_of_frame = Number_of_RF_rows[i]*Length_of_RF_row[i]
     
   bytes_to_read = f.read(3*Number_of_RF_rows[i] * 4)
   array = struct.unpack("="+str(3*Number_of_RF_rows[i])+"i", bytes_to_read)
   array = list(array)

   angle[i] = array[2::3]
   beam_x[i] =array[0::3]
   beam_y[i] =array[1::3]

   for j in range(Number_of_RF_rows[i]):
      angle[i][j] = float(angle[i][j])/1000000
      beam_x[i][j] = float(beam_x[i][j])/10000+(float(start_depth[i])/10*math.sin(angle[i][j]))
      beam_y[i][j] = float(beam_y[i][j])/10000+(float(start_depth[i])/10*math.cos(angle[i][j]))

   if (source_ID != 4):
    bytes_to_read = f.read(size_of_frame * 2)
    array = struct.unpack("="+str(size_of_frame)+"h", bytes_to_read)
    array = list(array)

    RF_data_arr[i]=array

   else:
    bytes_to_read = f.read(size_of_frame * 2)
    array = struct.unpack("="+str(size_of_frame)+"h", bytes_to_read)
    array = list(array)

    RF_data_arr[i]=array

    bytes_to_read = f.read(size_of_frame * 2)
    array = struct.unpack("="+str(size_of_frame)+"h", bytes_to_read)
    array = list(array)

    RF_data_arrQ[i]=array
    size_of_frame = size_of_frame*2

   size_in_bytes_run=(11*4)+(3*Number_of_RF_rows[i]*4)+(size_of_frame*2)
   size_in_bytes_global=size_in_bytes_global+size_in_bytes_run
   i=i+1;

   if ((statinfo.st_size-size_in_bytes_global)>=size_in_bytes_run):
      stop = 1
   else:
      stop = 0

 if (file_type==compare_toRF001):
  # read RF data file
  while stop==1:

   bytes_to_read = f.read(11 * 4)
   array = struct.unpack("11i", bytes_to_read)
   array = list(array)

   number_of_frames = array[0]
   header_size = array[1]
   frame_size = array[2]
   source_ID = array[3]
   tx_frequency[i] = array[4]
   frame_rate[i] = float(array[5])/100
   Length_of_RF_row[i] = array[6]
   Number_of_RF_rows[i]=array[7]
   Sampling_period_ns[i]=array[8]
   BIT_ADC[i] = array[9]
   start_depth[i] = array[10]
   size_of_frame = Number_of_RF_rows[i]*Length_of_RF_row[i]
     
   bytes_to_read = f.read(3*Number_of_RF_rows[i] * 4)
   array = struct.unpack("="+str(3*Number_of_RF_rows[i])+"i", bytes_to_read)
   array = list(array)

   angle[i] = array[2::3]
   beam_x[i] =array[0::3]
   beam_y[i] =array[1::3]

   for j in range(Number_of_RF_rows[i]):
      angle[i][j] = float(angle[i][j])/1000000
      beam_x[i][j] = float(beam_x[i][j])/10000+(float(start_depth[i])/10*math.sin(angle[i][j]))
      beam_y[i][j] = float(beam_y[i][j])/10000+(float(start_depth[i])/10*math.cos(angle[i][j]))
  
   bytes_to_read = f.read(size_of_frame * 2)
   array = struct.unpack("="+str(size_of_frame)+"h", bytes_to_read)
   array = list(array)

   RF_data_arr[i]=array

   size_in_bytes_run=(11*4)+(3*Number_of_RF_rows[i]*4)+(size_of_frame*2)
   size_in_bytes_global=size_in_bytes_global+size_in_bytes_run
   i=i+1;

   if ((statinfo.st_size-size_in_bytes_global)>=size_in_bytes_run):
     stop = 1
   else:
     stop = 0



 else:
  while stop==1:
   f1 = open(filename, "rb")
   bytes_to_read = f1.read(7 * 4)
   array = struct.unpack("7i", bytes_to_read)
   array = list(array)

   tx_frequency[i] = array[0]
   frame_rate[i] = float(array[1])/100
   Length_of_RF_row[i] = array[2]
   Number_of_RF_rows[i]=array[3]
   Sampling_period_ns[i]=array[4]
   BIT_ADC[i] = array[5]
   start_depth[i] = array[6]
   size_of_frame = Number_of_RF_rows[i]*Length_of_RF_row[i]
     
   bytes_to_read = f1.read(3*Number_of_RF_rows[i] * 4)
   array = struct.unpack("="+str(3*Number_of_RF_rows[i])+"i", bytes_to_read)
   array = list(array)

   angle[i] = array[2::3]
   beam_x[i] =array[0::3]
   beam_y[i] =array[1::3]

   for j in range(Number_of_RF_rows[i]):
      angle[i][j] = float(angle[i][j])/1000000
      beam_x[i][j] = float(beam_x[i][j])/10000+(float(start_depth[i])/10*math.sin(angle[i][j]))
      beam_y[i][j] = float(beam_y[i][j])/10000+(float(start_depth[i])/10*math.cos(angle[i][j]))
  
   bytes_to_read = f1.read(size_of_frame * 2)
   array = struct.unpack("="+str(size_of_frame)+"h", bytes_to_read)
   array = list(array)

   RF_data_arr[i]=array

   size_in_bytes_run=(7*4)+(3*Number_of_RF_rows[i]*4)+(size_of_frame*2)
   size_in_bytes_global=size_in_bytes_global+size_in_bytes_run
   i=i+1;

   if ((statinfo.st_size-size_in_bytes_global)>=size_in_bytes_run):
     stop = 1
   else:
     stop = 0

def clicked():
 
    res = "Frame rate: " + str(frame_rate[int(txt.get())])
    lbl.configure(text= res)

    res1 = "tx_frequency: " + str(tx_frequency[int(txt.get())]/1000000)   
    lbl1.configure(text= res1)

    res1 = "Length_of_RF_row: " + str(Length_of_RF_row[int(txt.get())])   
    lbl2.configure(text= res1)

    res1 = "Number of RF rows: " + str(Number_of_RF_rows[int(txt.get())])   
    lbl5.configure(text= res1)

    res1 = "Number of recorded frames: " + str(i)   
    lbl6.configure(text= res1)

    res1 = "Sampling period ns: " + str(Sampling_period_ns[int(txt.get())])   
    lbl7.configure(text= res1) 
    
    global reshaped
    reshaped = {}
    reshapedQ = {}
    frame_num = 0 # Number of the selected frame 
    # reshape RF data array of the selected frame to a 2D matrix
    reshaped = numpy.reshape(RF_data_arr[int(txt.get())][0:size_of_frame],(Number_of_RF_rows[int(txt.get())],Length_of_RF_row[int(txt.get())]))

    if (source_ID == 4):
      reshapedQ = numpy.reshape(RF_data_arrQ[int(txt.get())][0:size_of_frame],(Number_of_RF_rows[int(txt.get())],Length_of_RF_row[int(txt.get())]))

    matplotCanvas(window,reshaped,reshapedQ)
    
btn = Button(window, text="Show", command=clicked)
btn.grid(column=5, row=0)

new_item.add_command(label='Load RF data', command=clicked3)
menu.add_cascade(label='File', menu=new_item)
 
window.config(menu=menu)

def matplotCanvas(window,reshaped,reshapedQ):
    f = Figure(figsize=(6,5),dpi=100)
    a = f.add_subplot(111)
    a.plot(reshaped[int(txt1.get())][0:Length_of_RF_row[int(txt.get())]])
    if (source_ID == 4):
       a.plot(reshapedQ[int(txt1.get())][0:Length_of_RF_row[int(txt.get())]]) 
    from scipy.signal import hilbert
    hilbert_transformed = hilbert(reshaped[int(txt1.get())][0:Length_of_RF_row[int(txt.get())]])
    absolute_value = numpy.abs(hilbert_transformed) 
    a.plot(absolute_value)
    a.set_xlabel('Samples')
    a.set_ylabel('ADC units')
    a.set_title('RF data row and its envelope')

    canvas = FigureCanvasTkAgg(f,window)
    canvas.draw()
    canvas.get_tk_widget().grid(row=11,column=7)

    toolbar_frame = Frame(window)
    toolbar_frame.grid(row=21,column=6,columnspan=2)
    toolbar = NavigationToolbar2Tk( canvas, toolbar_frame )


lbl = Label(window, text="Frame rate: ", relief=RIDGE)
lbl.grid(column=3, row=0, sticky=NSEW)
lbl1 = Label(window, text="tx frequency: ",relief=RIDGE)
lbl1.grid(column=3, row=1, sticky=NSEW)

lbl2 = Label(window, text="Length of RF row: ",relief=RIDGE)
lbl2.grid(column=3, row=2, sticky=NSEW)

lbl5 = Label(window, text="Number of RF rows: ",relief=RIDGE)
lbl5.grid(column=3, row=3, sticky=NSEW)

lbl6 = Label(window, text="Number of recorded frames: ",relief=RIDGE)
lbl6.grid(column=3, row=4, sticky=NSEW)

lbl7 = Label(window, text="Sampling period ns: ",relief=RIDGE)
lbl7.grid(column=3, row=5, sticky=NSEW)

lbl3 = Label(window, text="Frame to show: ")
lbl3.grid(column=4, row=0)

txt = Entry(window,width=10)
txt.grid(column=4, row=1)

lbl4 = Label(window, text="Row to show: ")
lbl4.grid(column=4, row=2)

txt1 = Entry(window,width=10)
txt1.grid(column=4, row=3) 
 
window.mainloop()
