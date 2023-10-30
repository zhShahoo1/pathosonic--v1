import os 
import numpy as np 


def dicom_write_slice(arr, dicom_file, idx, filename, e_r):
    arr = np.flip(arr, axis = 0)
    arr = np.uint16(256 * arr)
    
    # update header of dicom file
    dicom_file.Rows = arr.shape[0]
    dicom_file.Columns = arr.shape[1]
    dicom_file.PixelData = arr.tobytes()
    dicom_file.ImagePositionPatient = [0, 0, e_r * idx]

    # save as dicom slice 
    result = 1
    while result is not None:
        try:
            result = dicom_file.save_as(os.path.join(filename, f'slice{idx}.dcm'))
        except: 
            pass 