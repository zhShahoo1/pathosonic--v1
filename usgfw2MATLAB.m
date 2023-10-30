clear all
close all
clc

% image parameters (w - width, h - height)
w = 512; % image width in pixels
h = 512; % image height in pixels

path = 'D:\DARBAS\Real_time_matlab\Real-time_imaging_for_the_research\usgfw2wrapper_C++_sources\usgfw2wrapper\x64\Release\usgfw2wrapper.dll'; % path to dll library which operates between MATLAB and usgfw2 SDK
hfile = 'D:\DARBAS\Real_time_matlab\Real-time_imaging_for_the_research\usgfw2wrapper_C++_sources\usgfw2wrapper\usgfw2wrapper.h'; % path to h file of library which operates between MATLAB and usgfw2 SDK

% checking if library is loaded and loading if not
if not(libisloaded('USGFW2MATLABWRAPPER'))
   loadlibrary(path,hfile,'alias', 'USGFW2MATLABWRAPPER')
end

% List of available functions
libfunctions USGFW2MATLABWRAPPER -full
calllib('USGFW2MATLABWRAPPER','on_init') % function initializes variables used in scripts

[ERR_CODE1] = calllib('USGFW2MATLABWRAPPER','init_ultrasound_usgfw2'); % function creates main Usgfw2 library object

if (ERR_CODE1 == 2)
    errordlg('Main Usgfw2 library object not created');
    calllib('USGFW2MATLABWRAPPER','Close_and_release')        % function releases all initialized controls and variables 
    unloadlibrary USGFW2MATLABWRAPPER
    return;
end

[ERR_CODE2] = calllib('USGFW2MATLABWRAPPER','find_connected_probe'); % function detects connected probe

if (ERR_CODE2 ~= 101)
    errordlg('Probe not detected');
    calllib('USGFW2MATLABWRAPPER','Close_and_release')        % function releases all initialized controls and variables 
    unloadlibrary USGFW2MATLABWRAPPER
    return;
end

[ERR_CODE3] = calllib('USGFW2MATLABWRAPPER','data_view_function'); % function creates main ultrasound scanning object for selected probe 
if (ERR_CODE3 < 0)
    errordlg('Main ultrasound scanning object for selected probe not created');
    calllib('USGFW2MATLABWRAPPER','Close_and_release')        % function releases all initialized controls and variables
    unloadlibrary USGFW2MATLABWRAPPER
    return;
end

[ERR_CODE4] = calllib('USGFW2MATLABWRAPPER','mixer_control_function',0,0,w,h,0,0,0); % function creates B mixer control, passed parameters 
% are image width and height, then RGB values for background (0,0,0)-black
if (ERR_CODE4 < 0)
    errordlg('B mixer control not returned');
    calllib('USGFW2MATLABWRAPPER','Close_and_release')        % function releases all initialized controls and variables 
    unloadlibrary USGFW2MATLABWRAPPER
    return;
end


%% Get pixel size (resolution) and make the axis of ultrasound image
res_X = libpointer('singlePtr', zeros(1,1));
res_Y = libpointer('singlePtr', zeros(1,1));
calllib('USGFW2MATLABWRAPPER','get_resolution',res_X,res_Y) % function returns pixel size in x and y dimensions in mm

if (mod(w,2) == 0) 
X_axis = (-w/2+0.5:w/2-0.5).*res_X.Value;
else
X_axis = (-w/2:w/2).*res_X.Value; 
end
Y_axis = (0:h-1).*res_Y.Value;

old_resolution_x = res_X.Value;
old_resolution_y = res_X.Value; 

freeze = false;
p = libpointer('uint32Ptr', zeros(1,w*h*4)); 
iteration = 0; 
run_loop = true;
threshold = 1000; %% number of iterations to break imaging loop

calllib('USGFW2MATLABWRAPPER','return_pixel_values',p) % % function returns buffer with pixel values of current frame
Blue_component = p.Value(1:4:end); % extraction of one of the components (blue in example)
img_gsc = reshape(Blue_component',[w h]); % 1D buffer reshaping into image matrix

figure(1)
update_figure = image(X_axis,Y_axis,img_gsc(:,end:-1:1)')
colormap gray
caxis([0 255])
xlabel('Width [mm]')
ylabel('Depth [mm]')
axis equal

while (run_loop)
tic 
calllib('USGFW2MATLABWRAPPER','get_resolution',res_X,res_Y)

if (res_X.Value~=old_resolution_x || res_Y.Value~=old_resolution_y)
if (mod(w,2) == 0) 
X_axis = (-w/2+0.5:w/2-0.5).*res_X.Value;
else
X_axis = (-w/2:w/2).*res_X.Value; 
end
Y_axis = (0:h-1).*res_Y.Value;
old_resolution_x = res_X.Value;
old_resolution_y = res_X.Value; 
end

calllib('USGFW2MATLABWRAPPER','return_pixel_values',p) % % function returns buffer with pixel values of current frame
Blue_component = p.Value(1:4:end); % extraction of one of the components (blue in example)
img_gsc = reshape(Blue_component',[w h]); % 1D buffer reshaping into image matrix

figure(1)
set(update_figure, 'XData',X_axis)
set(update_figure, 'YData',Y_axis)
set(update_figure, 'CData',img_gsc(:,end:-1:1)')
axis equal

time = toc;

FPS = int32(1/time); % Frames per second counter
title(['FPS = ', num2str(FPS)])

iteration = iteration + 1;
if (iteration > threshold)
   run_loop = false;
   calllib('USGFW2MATLABWRAPPER','Freeze_ultrasound_scanning')  %% function to freeze scanning   
   calllib('USGFW2MATLABWRAPPER','Stop_ultrasound_scanning') % function stops ultrasound scanning
   calllib('USGFW2MATLABWRAPPER','Close_and_release')        % function releases all initialized controls and variables 
   unloadlibrary USGFW2MATLABWRAPPER                         % DLL library unload
   return;
end
end


return
%% Note: these functions must be called for sucessfull re-runing of the script (even if you stopped imaging loop manulaly by Ctrl+C, you must call these functions)
calllib('USGFW2MATLABWRAPPER','Stop_ultrasound_scanning') % function stops ultrasound scanning
calllib('USGFW2MATLABWRAPPER','Close_and_release')        % function releases all initialized controls and variables 
unloadlibrary USGFW2MATLABWRAPPER                         % DLL library unload

