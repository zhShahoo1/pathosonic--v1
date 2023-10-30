from dicomwritevolume import dicom_write_slice
import imageio
import numpy as np
from skimage.color import rgb2gray
import cv2
import os  
from skimage.feature import peak_local_max
import os 
from skimage.io import imread
from datetime import datetime 
import pandas as pd 
import time 

def make_volume(processdir, video_file, video_type, config_file, use_grid, marker_pos, calibrate):
    # -------------------------- Read Frames -------------------------- #

    print("Initializing")

    # read video file as either png frames or video file 
    if video_type == "mp4":
        print("Read Video file ")
        obj = imageio.get_reader(video_file,  'ffmpeg')
        vid = np.array(list(obj.iter_data()))

        # read frames and convert to rgb 
        frames = vid.shape[0]
        v = np.zeros((vid.shape[1], vid.shape[2], frames))
        print("Read the frames")
        for x in (range(frames)):
            v[:, :, x] = rgb2gray(vid[x])

    elif video_type == "frames":
        print("Reading folder with png frames")
        png_frames = sorted(os.listdir(video_file), key = len)
        frames = len(png_frames)
        test_im = imread(os.path.join(video_file, png_frames[0]))
        v = np.zeros((test_im.shape[0], test_im.shape[1], frames))

        
        if test_im.ndim == 2:
            # not RGB
            for x, im in (enumerate(png_frames)):
                v[:, :, x] = imread(os.path.join(video_file, im)).astype(float)
        else: 
            # RGB 
            for x, im in (enumerate(png_frames)):
                v[:, :, x] = rgb2gray(imread(os.path.join(video_file, im)).astype(float))

    else: 
        print("Invalid video type")
        return None 



    # -------------------------- Scaling Factors -------------------------- #

    # read configuration file 
    if config_file is not None: 
        configurations = pd.read_csv(config_file, header = None)
        y_res = float(configurations.iloc[:, 0][11].split(":")[1][:-1]) # update it config file is updated 
        x_res = float(configurations.iloc[:, 0][10].split(":")[1][:-1]) # update it config file is updated
        e_r = float(configurations.iloc[:, 0][2].split(":")[1][:-1])    # update it config file is updated

        # d1 = 10/y_res
        # d2 = d1         # is x_res but x_res = y_res 
        # d3 = 10/e_r  
        scales_config = [y_res, x_res, e_r]
    
    if use_grid or calibrate:
        # find d1 
        global ix, iy, sx, sy
        ix, iy, sx, sy = -1,-1,-1,-1
        def draw_line(event, x, y, flags, param):
            global ix, iy, sx, sy

            if event == cv2.EVENT_LBUTTONDOWN:
                cv2.circle(frame, (x, y), 1, (200, 0, 0))

                if ix != -1: # if they are not the first points draw a line
                    cv2.line(frame, (ix, iy), (x, y), (200, 0, 0), 2, cv2.LINE_AA)
                else:
                    # if they are first points store as first points
                    sx, sy = x, y
                ix, iy = x, y

        frame = v[:, :, 1].copy()

        cv2.namedWindow('Draw 1 cm line')
        cv2.moveWindow('Draw 1 cm line', 600, 10)
        cv2.setMouseCallback('Draw 1 cm line' , draw_line)


        while(1):
            cv2.imshow('Draw 1 cm line', frame)
            if cv2.waitKey(1) == ord('q'):
                break
        d1 = np.sqrt((ix - sx) ** 2 + (iy - sy)**2) 

        # find d2 and d3 
        # global tx, ty
        # tx, ty = -1,-1
        # def draw_point(event, x, y, flags, param):
        #     global tx, ty

        #     if event == cv2.EVENT_LBUTTONDOWN:
        #         cv2.circle(slce, (x, y), 5, (200, 0, 0))
        #         tx, ty = x, y
        print("Find other scaling factors")
        slce = v[marker_pos].copy()

        # cv2.namedWindow('Draw point betwen specimen and scale')
        # cv2.moveWindow('Draw point betwen specimen and scale', 600, 10)
        # cv2.setMouseCallback('Draw point betwen specimen and scale' , draw_point)


        # while(1):
        #     cv2.imshow('Draw point betwen specimen and scale', slce)
        #     if cv2.waitKey(1) == ord('q'):
        #         break

        cv2.destroyAllWindows()
        # # row = ty
        # col = tx 

        # remove specimen 
        # slce[:, 500:1250] = 0 
        scales_left = slce[:, :500]  # will this be constant?
        scales_right = slce[:, 1250:] # will this be constant 

        def find_distance(im_bin, axis):
            im_sum = np.sum(im_bin, axis = axis)

            # find the four peaks 
            dist = 2
            idx = peak_local_max(im_sum, min_distance = dist)
            while len(idx) != 2: # 4:
                dist += 2
                idx = peak_local_max(im_sum, min_distance=dist).ravel()

            # find distance as an average over the 3 candidates in pixels
            idx = np.sort(idx, axis = 0)
            dist = idx[1] - idx[0] # np.mean(idx[1:] - idx[:3])

            return dist

        dist_vertical = dist_horizontal = np.mean([find_distance(scales_left, axis = 1), find_distance(scales_right, axis = 1)]) # find_distance(slce, axis = 1)
        dist_horizontal = dist_horizontal = np.mean([find_distance(scales_left, axis = 0), find_distance(scales_right, axis = 0)]) # find_distance(slce, axis = 0)


        # convert from pixels to mm 
        scale1 = 10 / d1 
        scale2 = 13 / dist_vertical
        scale3 = 13 / dist_horizontal

        scales_grid = np.array([scale1, scale2, scale3])

    print("Creating the dicom volume")

    # - - - - - - - save to dicom - - - - - - - #
    start_time = time.time()
    fname = "dicom_series"
    scales = scales_config if config_file is not None else scales_grid
    dicom_write_volume(frames, v, scales, processdir, fname)
    end_time = time.time()

    print(f"Time to create dicom volume: {(end_time - start_time):2.2f} seconds")

    # -------------------------- Create the text about the info -------------------------- #
    print("Create txt file about info")
    txt = os.path.join(processdir, "info.txt")
    
    if config_file is not None: # other things from config file can be added perhaps 
        with open(txt, "w") as fileID:
            fileID.write("Path: {0}\n".format(processdir))
            fileID.write("Number of frames: {0}\n".format(frames))
            fileID.write("Filename: {0}\n".format(processdir.split(os.sep)[-1]))
            fileID.write("Volume scales: {0}\n".format(np.round(scales, 4)))

            if calibrate:
                fileID.write("Calibration using scales: {0}\n".format(np.round(scales_grid, 4)))
                fileID.write('Copy right - File generated by Fatemeh Makouei (fatemeh.makouei@regionh.dk)')
                fileID.close()
    else: # using grid 
        with open(txt, "w") as fileID:
            fileID.write("Path: {0}\n".format(processdir))
            fileID.write("Duration: {0}\n".format(obj.get_meta_data('Scan')['duration']))
            fileID.write("Number of frames: {0}\n".format(frames))
            fileID.write("Filename: {0}\n".format(processdir.split("\n")[-1]))
            fileID.write("Volume scales: {0}\n".format(np.round(scales, 4)))
            fileID.write("FrameRate: {0}\n".format(obj.get_meta_data('Scan')['fps']))
          
            fileID.write('Copy right - File generated by Fatemeh Makouei (fatemeh.makouei@regionh.dk)')
            fileID.close()

    return "Done"