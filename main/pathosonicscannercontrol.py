import serial
import time

import serial.tools.list_ports


Ymax = 118
Xmax = 118
Zmax = 160

#Container center
offsetY = -5.5
offsetX = -5.5

#Scan speed (hardcoded, but dynamic later. 11.4.23)
scanspeed = 90 #mm/min ## mm/min (25hz and e_r) UPDATE CONFIG when changed in this library


def autocomport():
    print('Search...')
    ports = serial.tools.list_ports.comports(include_links=False)
    for port in ports :
        print('Find port ', port.device,port,"USB-SERIAL CH340" in str(port))

        if "USB-SERIAL CH340" in str(port):

            print('OK')
            return str(port.device)




################################################SERIAL PORT ASSIGNMENT############################################
serialport_act = autocomport()
# serialport_act = "COM5" # Uncomment this for manual assignment
################################################SERIAL PORT ASSIGNMENT############################################



def getresponse(serialconn):
    time.sleep(1)
    resp = serialconn.readline()
    return resp

def waitresponses(serialconn,mytext):
    resp = b'!'
    success = False
    while resp.decode() != "":
        resp = getresponse(serialconn)
        print(mytext , resp)
        if "ok" in resp.decode():
            success = True
            break
    return success

def returnresponses(serialconn,mytext):
    resp = b'!'
    success = False
    resps = []
    while resp.decode() != "":
        resp = getresponse(serialconn)
        print(mytext , resp)
        resps.append(resp.decode())
        if "ok" in resp.decode():
            success = True
            break
    return resps


def gettemperature(serialconn):
    
    serialconn.write(str.encode("M105 \r\n"))
    time.sleep(.5)
    resp = serialconn.readline()
    
    resp_split = str(resp).split(" ")
    T1_r = resp_split[1].split(":")[1]
    T2_r = resp_split[3].split(":")[1]
    T1 = float(T1_r)
    T2 = float(T2_r)
    return T1,T2

def home(serialconn,axis):
    if not axis in ["X","Y","Z"]:
        print("Invalid axis ID: ", axis)
        return False
    
    serialconn.write(str.encode("G28 "+str(axis)+"; \r\n"))

    scs = waitresponses(serialconn, "home "+axis+" : ")

    return scs

def feedrate(serialconn,Feedrate):
    serialconn.write(str.encode("G0 F" + str(Feedrate) + "; \r\n"  ))
    scs = waitresponses(serialconn,"FEEDRATE: ")
    return scs


def move(serialconn,axis,postion):
    if not axis in ["X","Y","Z"]:
        print("Invalid axis ID: ", axis)
        return False

    try:
        D = int(postion)
    except:
        print("Invalid distance ", postion)
        return False

    serialconn.write(str.encode("G0 " + str(axis) +str(D)+ "; \r\n"  ))
    scs = waitresponses(serialconn,"MOVE: ")
    return scs

    
def getposition_all(ser):
    ser.write(str.encode("M114 R; \r\n"  ))
    scs = getresponse(ser)
    return scs

def getposition_axis(ser,axis):
    '''Get position on axis'''
    if not axis in ["X","Y","Z"]:
        print("Invalid axis ID: ", axis)
        return False

    pos_all = getposition_all(ser)
    pos_all = str(pos_all).split(" ")

    for p in pos_all:
        print(p)
        if axis in p:
            position = float(p.split(":")[-1])
            break

    return position    

def connectprinter():
    ser = serial.Serial(serialport_act, 115200,timeout=1)
    return ser




def homeZ():
    '''Moves probe to center before homing. Assumes no container is in.'''


    #Center probe
    go2INIT()

    #Connect
    ser = connectprinter()

    try:
        scs_cmd = home(ser,"Z")
        scs = waitresponses(ser, "homeZ " )

    finally:
        ser.close()

def deltaMove(delta,axis):
    '''Move [delta] mm on [axis]'''

    if not axis in ["X","Y","Z"]:
        print("Invalid axis ID: ", axis)
        return False


    #Connect
    ser = connectprinter()
    pos = getposition_axis(ser,axis)
    print("MY POS:", pos)
    newposition = pos + delta

    if axis in ["Y","X"]:
        if newposition > Ymax:
            print("POS MAX REACHED 118mm",axis)
            newposition = Ymax
    elif axis == "Z":
        if newposition > Zmax:
            print("POS MAX REACHED 160mm",axis)
            newposition = Zmax

    if newposition < 0: newposition =0 


    move(ser,axis,newposition)


    return 1

#deltaMove(10,"Y")

def go2INIT():
    '''No assumptions of probe location. Homes probe and goes to INIT'''

    #Connect
    ser = connectprinter()

    try:
        #Zero
        scs_cmd = home(ser,"X")
        scs_cmd = home(ser,"Y")
        time.sleep(2)
        feedrate(ser,1000)
        scs = waitresponses(ser, "feedrate INIT" )


        #Go to
        Ypos = offsetY + (Ymax / 2)
        Xpos = offsetX + (Xmax / 2)

        mycmd = "G1 X"+str(Xpos)+" Y"+str(Ypos) + "; \r\n"
        ser.write(mycmd.encode())
        scs = waitresponses(ser, "move INIT" )

    finally:
        ser.close()

    return True



def go2StartScan():
    '''Assumes present position of probe is INIT. Moves only X axis to allow for manual adjustment'''

    #Connect
    ser = connectprinter()

    try:
        #Set scaning speed (Probe movement speed)
        mms = 20*60 # 20 mm/s converted to mm/min
        feedrate(ser,mms)



        mycmd = "G1 X"+str(0) + "; \r\n"
        ser.write(mycmd.encode()) 
        scs = waitresponses(ser, "move StartScan " )


    finally:
        ser.close()


    return True




def ScanPath():
    '''Moves probe in the entire scanning range at given speed'''

    #Connect
    ser = connectprinter()
    try:
        #Set scaning speed (Probe movement speed)
        feedrate(ser,scanspeed)

        Xpos = Xmax

        mycmd = "G1 X"+str(Xpos) + "; \r\n"
        ser.write(mycmd.encode())
        scs = waitresponses(ser, "move ScanPath " )

    finally:
        ser.close()




def get_position():
    #Connect
    ser = connectprinter()
    try:
        mycmd = "M114;"+  "\r\n"
        ser.write(mycmd.encode())
        scs = returnresponses(ser, "get pos " )

    finally:
        ser.close()

    return scs


#print("return", get_position())

#homeZ()

#go2INIT()
#time.sleep(3)
#go2StartScan()
#time.sleep(2)
#ScanPath()

def unknowns():
    #Fatemeh feed rate 0.1mm/s = 6 mm/min

    with serial.Serial('COM3', 115200,timeout=1) as ser:
        time.sleep(2)
        
        scs_cmd = home(ser,"X")
        scs_cmd = home(ser,"Y")
        scs_cmd = feedrate(ser,100)
        time.sleep(2)

        
        time.sleep(1)
        D = 0
        for i in range(15):
            D += 1
            scs_cmd =move(ser,"X",D)
            scs_cmd = getposition(ser)
            time.sleep(.2)
        
        #for i in range(0,5):
        #    T1,T2 = gettemperature(ser)
        #    print("Temperatures: ", T1, T2)
            #ser.write(str.encode("M117 "+str(i)+"\r\n"))
        #    time.sleep(1)
