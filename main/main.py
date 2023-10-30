
import os
import time
import subprocess as sp
import cam


from flask import Flask,render_template,Response
from flask_socketio import SocketIO, emit, disconnect



import pathosonicscannercontrol as pssc

# Theresa's import
from make_volume import make_volume

#CATCH "Probe not detected" at init. Fidn in record.py
#Get CAM number
#get serial COM port numbe
#pssc.go2INIT()


#File to enable waiting in multiscan.
with open("scanning","w") as fs:
	fs.write("0")


# Path to scriptb
myp = os.path.dirname(__file__) + os.sep
print("My path: ",myp)



#App initialization
app = Flask(__name__)

#socket_ = SocketIO(app, async_mode=async_mode)




@app.route('/start')
def start():

	name="PathoSonic P.T."

	instructions = [
	"1. Make sure probe is...",
	"2. Fingers away",
	"56. Confirm"
	]

	return render_template('start.html', name=name,instr_list=instructions)


@app.route('/incY')
def Yplus():
	pssc.deltaMove(2,"Y")
	return "Yplus"

@app.route('/decY')
def Yminus():
	pssc.deltaMove(-2,"Y")
	return "Yminus"

@app.route('/incZ')
def Zplus():
	pssc.deltaMove(5,"Z")
	return "Zplus"

@app.route('/decZ')
def Zminus():
	pssc.deltaMove(-5,"Z")
	return "Zminus"



@app.route('/main')
def main():
	name="Main window"
	return render_template('main.html', name=name)


@app.route('/initscanner')
def initscanner():
	pssc.go2INIT()
	return "Inits"

@app.route('/scanpath')
def startcmd():
	startscan(False)
	myfile = getdatafolders()
	mylink = "'" + myp + os.sep + "data" + os.sep + myfile + "'"

	return render_template('scanning.html', link2files=mylink, linkshort=myfile)



@app.route('/multipath')
def startmulti():
	multiscan()
	myfile = getdatafolders() + "MULTISCAN"
	mylink = "'" + myp + os.sep + "data" + os.sep + myfile + "'"

	return render_template('scanning.html', link2files=mylink, linkshort=myfile)



def getdatafolders():
	newest = 0
	for myfile in os.listdir(myp +os.sep +"static"+ os.sep + "data"):
		if int(myfile) > int(newest): newest = myfile
	return newest


@app.route('/video_feed')
def video_feed():
	return Response(cam.gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')



def startscan(multi):
	#Move to StartScan
	pssc.go2StartScan()

	time.sleep(4) #Movement to SS

	#Initialize Frame capture
	if multi:
		print("MULTI WAIT 8")
		time.sleep(8) #Movement to SS
		sp.Popen(["py", myp + os.sep + "record.py", "1"])
	else:
		time.sleep(4) #Movement to SS
		sp.Popen(["py", myp + os.sep + "record.py", "0"])
		

	print("Recording of frames started")
	#time.sleep(5)
	time.sleep(9)#UPDATE CIONFIG when changed in MAIN. Change in record.py

	print("Moving probe")
	#Move probe - scanning range
	pssc.ScanPath()





def checkscanning():
	with open("scanning","r") as fs:
		scan = fs.readlines()[0]
	if scan == "1":
		scanning = True
	else: 
		scanning = False

	return scanning
		

def multiscan():

	#Scan1
	startscan(True)

	c=0
	while 1: 
		if not checkscanning(): break
		time.sleep(.5)
		if c%15 == 0:
			print(c,"waiting for conv to finish")
		c+=1

	#Move Y
	pssc.deltaMove(18,"Y")

	startscan(True)

# Theresa's contribution start
@app.route('/processing')
def Process():
	print("Processing of scan started")
	with open("recdir", 'r') as f: processdir = f.readlines()[0].split("\n")[0]
	f.close()

	video_type = "frames"
	path_to_scan = os.path.join(processdir, video_type)
	path_to_config_file = os.path.join(processdir, "config.txt")
	use_grid = 0
	calibrate = 0
	marker_pos = 815

	make_volume(processdir, path_to_scan, video_type, path_to_config_file, use_grid, marker_pos, calibrate)

	return "Done"

 
# Theresa's contribution end 


#@socket_.on('do_task', namespace='/test')


# main driver function
if __name__ == '__main__':

	# run() method of Flask class runs the application
	# on the local development server.
	app.run()

"""

if __name__ == "__main__":

	# run() method of Flask class runs the application
	#on actual network server 
	app.run(host="100.68.47.137", port=5000)
	"""