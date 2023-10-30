function varargout = GUI_MATLAB_usgfw2(varargin)
% GUI_MATLAB_USGFW2 MATLAB code for GUI_MATLAB_usgfw2.fig
%      GUI_MATLAB_USGFW2, by itself, creates a new GUI_MATLAB_USGFW2 or raises the existing
%      singleton*.
%
%      H = GUI_MATLAB_USGFW2 returns the handle to a new GUI_MATLAB_USGFW2 or the handle to
%      the existing singleton*.
%
%      GUI_MATLAB_USGFW2('CALLBACK',hObject,eventData,handles,...) calls the local
%      function named CALLBACK in GUI_MATLAB_USGFW2.M with the given input arguments.
%
%      GUI_MATLAB_USGFW2('Property','Value',...) creates a new GUI_MATLAB_USGFW2 or raises the
%      existing singleton*.  Starting from the left, property value pairs are
%      applied to the GUI before GUI_MATLAB_usgfw2_OpeningFcn gets called.  An
%      unrecognized property name or invalid value makes property application
%      stop.  All inputs are passed to GUI_MATLAB_usgfw2_OpeningFcn via varargin.
%
%      *See GUI Options on GUIDE's Tools menu.  Choose "GUI allows only one
%      instance to run (singleton)".
%
% See also: GUIDE, GUIDATA, GUIHANDLES

% Edit the above text to modify the response to help GUI_MATLAB_usgfw2

% Last Modified by GUIDE v2.5 13-May-2022 11:19:43

% Begin initialization code - DO NOT EDIT
gui_Singleton = 1;
gui_State = struct('gui_Name',       mfilename, ...
                   'gui_Singleton',  gui_Singleton, ...
                   'gui_OpeningFcn', @GUI_MATLAB_usgfw2_OpeningFcn, ...
                   'gui_OutputFcn',  @GUI_MATLAB_usgfw2_OutputFcn, ...
                   'gui_LayoutFcn',  [] , ...
                   'gui_Callback',   []);
if nargin && ischar(varargin{1})
    gui_State.gui_Callback = str2func(varargin{1});
end

if nargout
    [varargout{1:nargout}] = gui_mainfcn(gui_State, varargin{:});
else
    gui_mainfcn(gui_State, varargin{:});
end
% End initialization code - DO NOT EDIT


% --- Executes just before GUI_MATLAB_usgfw2 is made visible.
function GUI_MATLAB_usgfw2_OpeningFcn(hObject, eventdata, handles, varargin)
% This function has no output args, see OutputFcn.
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
% varargin   command line arguments to GUI_MATLAB_usgfw2 (see VARARGIN)

% Choose default command line output for GUI_MATLAB_usgfw2
handles.output = hObject;

global flag1; % flag to stop scanning and imaging if close X is pressed
flag1 = 0;

% disable "Run" button while ultrasound scanning is already running
set(handles.pushbutton1,'Enable','off')

handles.w = 512; % image width in pixels
handles.h = 512; % image height in pixels
path = 'D:\DARBAS\Real_time_matlab\Real-time_imaging_for_the_research\usgfw2wrapper_C++_sources\usgfw2wrapper\x64\Release\usgfw2wrapper.dll'; % path to dll library which operates between MATLAB and usgfw2 SDK
hfile = 'D:\DARBAS\Real_time_matlab\Real-time_imaging_for_the_research\usgfw2wrapper_C++_sources\usgfw2wrapper\usgfw2wrapper.h'; % path to h file of library which operates between MATLAB and usgfw2 SDK

% checking if library is loaded and loading if not
if not(libisloaded('USGFW2MATLABWRAPPER'))
   loadlibrary(path,hfile,'alias', 'USGFW2MATLABWRAPPER');
% libfunctions USGFW2MATLABWRAPPER -full

calllib('USGFW2MATLABWRAPPER','on_init'); % function initializes variables used in scripts
[ERR_CODE1] = calllib('USGFW2MATLABWRAPPER','init_ultrasound_usgfw2'); % function creates Main Usgfw2 library object

if (ERR_CODE1 == 2)
    errordlg('Main Usgfw2 library object not created');
    calllib('USGFW2MATLABWRAPPER','Close_and_release')
    unloadlibrary USGFW2MATLABWRAPPER
    return;
end

[ERR_CODE2] = calllib('USGFW2MATLABWRAPPER','find_connected_probe'); % function detecs connected probe

if (ERR_CODE2 ~= 101)
    errordlg('Probe not detected');
    calllib('USGFW2MATLABWRAPPER','Close_and_release')
    unloadlibrary USGFW2MATLABWRAPPER
    return;
end

[ERR_CODE3] = calllib('USGFW2MATLABWRAPPER','data_view_function'); % function creartes main ultrasound scanning object for selected probe 
if (ERR_CODE3 < 0)
    errordlg('Main ultrasound scanning object for selected probe not created');
    calllib('USGFW2MATLABWRAPPER','Close_and_release')
    unloadlibrary USGFW2MATLABWRAPPER
    return;
end

[ERR_CODE4] = calllib('USGFW2MATLABWRAPPER','mixer_control_function',0,0,handles.w,handles.h,0,0,0); % function creates B mixer control, passed parameters 
% are image width and hegth, then RGB values for background (0,0,0)-black
if (ERR_CODE4 < 0)
    errordlg('B mixer control not returned');
    calllib('USGFW2MATLABWRAPPER','Close_and_release')
    unloadlibrary USGFW2MATLABWRAPPER
    return;
end
end

%% Get pixel size (resolution) and make the axis of ultrasound image
res_X = libpointer('singlePtr', zeros(1,1));
res_Y = libpointer('singlePtr', zeros(1,1));
calllib('USGFW2MATLABWRAPPER','get_resolution',res_X,res_Y) % function returns pixel size in x and y dimensions in mm

if (mod(handles.w,2) == 0) 
X_axis = (-handles.w/2+0.5:handles.w/2-0.5).*res_X.Value;
else
X_axis = (-handles.w/2:handles.w/2).*res_X.Value; 
end
Y_axis = (0:handles.h-1).*res_Y.Value;

old_resolution_x = res_X.Value;
old_resolution_y = res_X.Value; 

handles.freeze = false;
p = libpointer('uint32Ptr', zeros(1,handles.w*handles.h*4)); 
handles.run_loop = true;

%% draw first image
calllib('USGFW2MATLABWRAPPER','return_pixel_values',p) % function returns buffer with pixel values of current frame
Blue_component = p.Value(1:4:end); % extraction of one of the components (blue in example)
img_gsc = reshape(Blue_component',[handles.w handles.h]); % 1D buffer reshaping into image matrix

axes(handles.axes_imaging);
update_figure = image(X_axis,Y_axis,img_gsc(:,end:-1:1)') % note returned ultrasound image are BGRA order and flipped 180 deg, so you have to use end:-1:1 for correct display
colormap gray
caxis([0 255])
xlabel('Width [mm]')
ylabel('Depth [mm]')
axis equal


while (handles.run_loop)
tic 
drawnow;
if (flag1 == 1)
   return;
end
if (get(handles.pushbutton2, 'userdata') == 1)
    handles.run_loop = false;  
end

calllib('USGFW2MATLABWRAPPER','get_resolution',res_X,res_Y)

if (res_X.Value~=old_resolution_x || res_Y.Value~=old_resolution_y)
if (mod(handles.w,2) == 0) 
X_axis = (-handles.w/2+0.5:handles.w/2-0.5).*res_X.Value;
else
X_axis = (-handles.w/2:handles.w/2).*res_X.Value; 
end
Y_axis = (0:handles.h-1).*res_Y.Value;
old_resolution_x = res_X.Value;
old_resolution_y = res_X.Value; 
end

calllib('USGFW2MATLABWRAPPER','return_pixel_values',p) % function returns buffer with pixel values of current frame
Blue_component = p.Value(1:4:end); % extraction of one of the components (blue in example)
img_gsc = reshape(Blue_component',[handles.w handles.h]); % 1D buffer reshaping into image matrix


set(update_figure, 'XData',X_axis)
set(update_figure, 'YData',Y_axis)
set(update_figure, 'CData',img_gsc(:,end:-1:1)')
axis equal

time = toc;
FPS = int32(1/time) % Frames per second counter
set(handles.FPS_indicator,'String', num2str(FPS))
end
% Update handles structure
guidata(hObject, handles);

% --- Outputs from this function are returned to the command line.
function varargout = GUI_MATLAB_usgfw2_OutputFcn(hObject, eventdata, handles) 
% varargout  cell array for returning output args (see VARARGOUT);
% hObject    handle to figure
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

% Get default command line output from handles structure
%varargout{1} = handles.output;


% --- Executes on button press in pushbutton1.
function pushbutton1_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

set(handles.pushbutton2,'Enable','on')
set(handles.pushbutton1,'Enable','off')

global flag1;
if (flag1 == 1)
    handles.run_loop = false;    
    return;
end

set(handles.pushbutton2, 'userdata',0);
calllib('USGFW2MATLABWRAPPER','Run_ultrasound_scanning')
%% Get pixel size (resolution) and make the axis of ultrasound image
res_X = libpointer('singlePtr', zeros(1,1));
res_Y = libpointer('singlePtr', zeros(1,1));
calllib('USGFW2MATLABWRAPPER','get_resolution',res_X,res_Y)

if (mod(handles.w,2) == 0) 
X_axis = (-handles.w/2+0.5:handles.w/2-0.5).*res_X.Value;
else
X_axis = (-handles.w/2:handles.w/2).*res_X.Value; 
end
Y_axis = (0:handles.h-1).*res_Y.Value;

old_resolution_x = res_X.Value;
old_resolution_y = res_X.Value; 

handles.run_loop = true;

p = libpointer('uint32Ptr', zeros(1,handles.w*handles.h*4)); 

calllib('USGFW2MATLABWRAPPER','return_pixel_values',p)
Blue_component = p.Value(1:4:end);
img_gsc = reshape(Blue_component',[handles.w handles.h]);

axes(handles.axes_imaging);
update_figure=image(X_axis,Y_axis,img_gsc(:,end:-1:1)');
colormap gray
caxis([0 255])
xlabel('Width [mm]')
ylabel('Depth [mm]')
axis equal


while (handles.run_loop)
tic 
drawnow;
if (flag1 == 1)
    handles.run_loop = false;    
    return;
end
if (get(handles.pushbutton2, 'userdata') == 1)
    handles.run_loop = false;   
end

calllib('USGFW2MATLABWRAPPER','get_resolution',res_X,res_Y)

if (res_X.Value~=old_resolution_x || res_Y.Value~=old_resolution_y)
if (mod(handles.w,2) == 0) 
X_axis = (-handles.w/2+0.5:handles.w/2-0.5).*res_X.Value;
else
X_axis = (-handles.w/2:handles.w/2).*res_X.Value; 
end
Y_axis = (0:handles.h-1).*res_Y.Value;
old_resolution_x = res_X.Value;
old_resolution_y = res_X.Value; 
end

calllib('USGFW2MATLABWRAPPER','return_pixel_values',p)
Blue_component = p.Value(1:4:end);
img_gsc = reshape(Blue_component',[handles.w handles.h]);

set(update_figure, 'CData',img_gsc(:,end:-1:1)');
time = toc;

FPS = int32(1/time);
set(handles.FPS_indicator,'String', num2str(FPS))
end
guidata(hObject, handles);


% --- Executes on button press in pushbutton2.
function pushbutton2_Callback(hObject, eventdata, handles)
% hObject    handle to pushbutton2 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)

set(handles.pushbutton1,'Enable','on')
set(handles.pushbutton2,'Enable','off')

set(handles.pushbutton2, 'userdata',1) 
handles.freeze = true;
calllib('USGFW2MATLABWRAPPER','Freeze_ultrasound_scanning')
guidata(hObject, handles);

% --- Executes when user attempts to close figure1.
function figure1_CloseRequestFcn(hObject, eventdata, handles)
% hObject    handle to figure1 (see GCBO)
% eventdata  reserved - to be defined in a future version of MATLAB
% handles    structure with handles and user data (see GUIDATA)
global flag1;
flag1 = 1;
if (libisloaded('USGFW2MATLABWRAPPER'))
calllib('USGFW2MATLABWRAPPER','Stop_ultrasound_scanning') % function stops ultrasound scanning
calllib('USGFW2MATLABWRAPPER','Close_and_release')        % function releases all initialized controls and variables 
unloadlibrary USGFW2MATLABWRAPPER                         % DLL library unload 
end
% Hint: delete(hObject) closes the figure
delete(hObject);