import os 
import pydicom
import numpy as np 
from tqdm import tqdm 

def convertNsave(arr, file_dir, index, scales):
    """
    arr     : array representing one slice 
    file_dir: directory to save slice 
    index   : index of slice in whole volume 
    scales  : scale in each axis
    """

    scale1, scale2, scale3 = scales[0], scales[1], scales[2]
    
    dicom_file = pydicom.dcmread('dcmimage.dcm')
    arr = np.uint16(256 * arr)
    dicom_file.Rows = arr.shape[0]
    dicom_file.Columns = arr.shape[1]
    dicom_file.PhotometricInterpretation = "MONOCHROME2"
    dicom_file.SamplesPerPixel = 1
    dicom_file.BitsStored = 16
    dicom_file.BitsAllocated = 16
    dicom_file.HighBit = 15
    dicom_file.PixelRepresentation = 0
    dicom_file.WindowCenter = 0 
    dicom_file.WindowWidth = 1000
    dicom_file.SOPClassUID = '1.2.840.10008.5.1.4.1.1.2'
    # dicom_file.TransferSyntaxUID = '1.2.840.10008.1.2.1'
    dicom_file.RescaleIntercept = -1024
    dicom_file.RescaleSlope = 1
    dicom_file.RescaleType = 'HU'
    dicom_file.SliceThickness = scale3
    dicom_file.ImagerPixelSpacing = [scale1, scale2]
    dicom_file.PixelSpacing = [scale1, scale2]
    dicom_file.PixelData = arr.tobytes()
    dicom_file.ImagePositionPatient = [0, 0, index * scale3]

    dicom_file.save_as(os.path.join(file_dir, f'slice{index}.dcm'))

def dicom_write_volume(frames, v, scales, save_name_folder, save_name_dicom, start = 0):
    to_save_path = os.path.join("Reconstructions", save_name_folder, save_name_dicom)


    os.makedirs(to_save_path, exist_ok=True)
    for idx in range(start, frames):
        try: 
            convertNsave(v[:, :, idx], to_save_path, idx, scales)
        except OSError:
            idx -= 1 

