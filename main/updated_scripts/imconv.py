import os
import numpy as np
from PIL import Image
import pydicom


from dicomwritevolume import dicom_write_slice

def tiff_force_8bit(image, **kwargs):
	if image.format == 'TIFF' and image.mode == 'I;16':
		array = np.array(image)
		normalized = (array.astype(np.uint16) - array.min()) * 255.0 / (array.max() - array.min())
		image = Image.fromarray(normalized.astype(np.uint8))

	return image

#Get dir
processdir = ""
with open("recdir",'r') as f: processdir = f.readlines()[0].split("\n")[0]
print(processdir)

if not os.path.exists(processdir + os.sep + "processed"):
	try:
		os.mkdir(processdir + os.sep + "frames")
		os.mkdir(processdir + os.sep + "raws")
		os.mkdir(processdir + os.sep + "dicom_series")
	except FileExistsError:
		pass

	for file in os.listdir(processdir):
		# read configuration file to get the resolutions
		configurations = pd.read_csv(os.path.join(processdir, "config.txt"), header = None)
        y_res = float(configurations.iloc[:, 0][11].split(":")[1][:-1]) # update it config file is updated 
        x_res = float(configurations.iloc[:, 0][10].split(":")[1][:-1]) # update it config file is updated
        e_r = float(configurations.iloc[:, 0][2].split(":")[1][:-1])    # update it config file is updated

		# prepare dicom header 
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
	    dicom_file.RescaleIntercept = -1024
	    dicom_file.RescaleSlope = 1
	    dicom_file.RescaleType = 'HU'  
	    dicom_file.SliceThickness = e_r 
	    dicom_file.ImagerPixelSpacing = [x_res, y_res]
	    dicom_file.PixelSpacing = [x_res, y_res]
		try:
			if file.endswith("npy"):
				tfile = np.load(processdir + os.sep + file)

				# save slice as dicom slice 
				dicom_write_slice(tfile, dicom_file, file.split(".")[0], os.path.join(processdir, "dicom_series"), e_r)

				#print(tfile.dtype)
				tfile = np.flipud(tfile)
				im = Image.fromarray(tfile)
				im2 = tiff_force_8bit(im)
				
				os.rename(processdir + os.sep +file, processdir +os.sep+"raws"+ os.sep + file)
				im2.convert('P').save(processdir + os.sep + "frames" + os.sep + file.split(".")[0]+".png")
		except PermissionError:
			pass


with open("scanning","w") as fs:
	fs.write("0")