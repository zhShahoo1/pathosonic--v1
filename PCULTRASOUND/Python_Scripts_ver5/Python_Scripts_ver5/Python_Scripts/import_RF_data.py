import struct
import os
import math
import scipy
import numpy
import matplotlib.pyplot as plt



filename = "14.42.33_11-04-2022_C5-2H60-A5.bin";
statinfo = os.stat(filename)
f = open(filename, "rb")

size_in_bytes_global=0
stop = 1;
i=0;
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
time_stamps = {}

bytes_to_read = f.read(1 * 6)
file_type = struct.unpack("6c", bytes_to_read)
compare_toRF001 = (b'R', b'F', b'0', b'0', b'0', b'1')
compare_toRF002 = (b'R', b'F', b'0', b'0', b'0', b'2')
compare_toRF003 = (b'R', b'F', b'0', b'0', b'0', b'3')
compare_toRF003 = (b'R', b'F', b'0', b'0', b'0', b'4')


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


reshaped = {}
reshapedQ = {}
frame_num = 0 # Number of the selected frame 
# reshape RF data array of the selected frame to a 2D matrix
reshaped = numpy.reshape(RF_data_arr[frame_num][0:size_of_frame],(Number_of_RF_rows[frame_num],Length_of_RF_row[frame_num]))
if (source_ID == 4):
 reshapedQ = numpy.reshape(RF_data_arrQ[frame_num][0:size_of_frame],(Number_of_RF_rows[frame_num],Length_of_RF_row[frame_num]))

Sampling_period_s = Sampling_period_ns[frame_num]*10**-9 # Sampling period in s

Speed_of_sound = 1540 # m/s
time_axis = [0 for j in range(Length_of_RF_row[frame_num])]
depth_axis = [0 for j in range(Length_of_RF_row[frame_num])]

for i in range(Length_of_RF_row[frame_num]):
    time_axis[i]=(i*Sampling_period_s) # scanning time axis, seconds (starting from 0)        
    depth_axis[i]=(time_axis[i]*0.5*Speed_of_sound)*100; # scanning depth axis, in cm (starting from 0) 
          
# Corrdinates for B mode imaging
x_axis = [[0 for i in range(Number_of_RF_rows[frame_num])] for i in range(Length_of_RF_row[frame_num])]
y_axis = [[0 for i in range(Number_of_RF_rows[frame_num])] for i in range(Length_of_RF_row[frame_num])]

if (angle[frame_num][0]==0): # linear probe
 for j in range(Number_of_RF_rows[frame_num]):
   for i in range(Length_of_RF_row[frame_num]):
       x_axis[i][j] = beam_x[frame_num][j] # Width axis (correct absolute coordinates of RF window), cm
       y_axis[i][j] = depth_axis[i]+beam_y[frame_num][j] # Depth axis (correct absolute coordinates of RF window), cm

else: # convex probe

 vector = [[0 for j in range(2)] for i in range(Length_of_RF_row[frame_num])]
 for i in range(Length_of_RF_row[frame_num]):
   vector[i][0] = depth_axis[i];
   vector[i][1] = 0

 for j in range(Number_of_RF_rows[frame_num]):
   angle_1=angle[frame_num][j];
   R =[[math.cos(angle_1), math.sin(angle_1)], [-math.sin(angle_1), math.cos(angle_1)]]
   out = numpy.matmul(vector,R)

   for i in range(Length_of_RF_row[frame_num]):
     x_axis[i][j] = out[i][0]+beam_y[frame_num][j] # Width axis (correct absolute coordinates of RF window), cm
     y_axis[i][j] = out[i][1]+beam_x[frame_num][j] # Depth axis (correct absolute coordinates of RF window), cm 


# Envelope detection
hilbert_transformed1 = [[0 for i in range(Length_of_RF_row[frame_num])] for i in range(Number_of_RF_rows[frame_num])]
from scipy.signal import hilbert
for i in range(Number_of_RF_rows[frame_num]):
   hilbert_transformed1[i] = (numpy.abs(hilbert(reshaped[i][0:Length_of_RF_row[frame_num]])))

# Logarithmic transform
log_transformed1 = [[0 for i in range(Length_of_RF_row[frame_num])] for i in range(Number_of_RF_rows[frame_num])]
for i in range(Number_of_RF_rows[frame_num]):
  for j in range(Length_of_RF_row[frame_num]):
      log_transformed1[i][j] = math.log10(hilbert_transformed1[i][j])

# Visualization 
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
fig = plt.figure(2)
ax = fig.add_subplot(111, projection='3d')

ax.plot_surface(x_axis, y_axis, numpy.transpose(numpy.array(log_transformed1)), rstride=1, cstride=1,
                cmap='gray', edgecolor='none');

if (angle[frame_num][0]==0):
  ax.view_init(elev=-90, azim=-90)
else:
  ax.view_init(elev=90, azim=360)

if (angle[frame_num][0]==0):
  ax.set_xlabel('Width, cm')
  ax.set_ylabel('Depth, cm')
else:
  ax.set_xlabel('Depth, cm')
  ax.set_ylabel('Width, cm')    

from scipy.signal import hilbert
hilbert_transformed = hilbert(RF_data_arr[0][0:Length_of_RF_row[0]])
absolute_value = numpy.abs(hilbert_transformed)

plt.figure()
plt.plot(reshaped[0][0:Length_of_RF_row[frame_num]])
if (source_ID == 4):
 plt.plot(reshapedQ[0][0:Length_of_RF_row[frame_num]])   
plt.plot(absolute_value)
plt.xlabel('Samples')
plt.ylabel('ADC units')
plt.title('RF data row and its envelope')
plt.show()
