import os
import numpy as np

from PIL import Image


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
	except FileExistsError:
		pass

	for file in os.listdir(processdir):
		#print(file)
		try:
			if file.endswith("npy"):
				tfile = np.load(processdir + os.sep +file)
				#print(tfile.dtype)
				tfile = np.flipud(tfile)
				im = Image.fromarray(tfile)
				im2 = tiff_force_8bit(im)
				
				os.rename(processdir + os.sep +file, processdir +os.sep+"raws"+ os.sep +file)
				#print(im)
				#print(processdir + os.sep + "frames")
				#im.save(processdir + os.sep + "frames" + os.sep + file.split(".")[0]+".tiff")
				#im.save(processdir + os.sep + "frames" + os.sep + file.split(".")[0]+".png")
				im2.convert('P').save(processdir + os.sep + "frames" + os.sep + file.split(".")[0]+".png")
		except PermissionError:
			pass


with open("scanning","w") as fs:
	fs.write("0")