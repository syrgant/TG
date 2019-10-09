import os
import subprocess
import serial
import time
import datetime
import serial.tools.list_ports
from tkinter import filedialog
from tkinter import *
import _thread
import matplotlib.animation as animation
import matplotlib
import csv
#set the backend to use and import navigation bar
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#import figure for graph
from matplotlib.figure import Figure
#use queues to communicate with animation
import queue
#make graph look better with style
from matplotlib import style
style.use("ggplot")

#get the calibrated equation from the file
global aCalA
global bCalA
global cCalA

global aCalB
global bCalB
global cCalB

AValData = []
BValData = []
DiscomfortData = []

try:
    manTemp = manualTemp.get(timeout=0)
    manualTemp.put(manTemp)
except:
    manualTemp = queue.Queue()
    manualTemp.put(True)


averageArray = [0, 1, 2, 3, 4, 5]

global tempsChanged

#calFile = open("CalibratedValues.txt", "r")

try:
    calFile = open("CalibratedValues.txt", "r")
    lines = calFile.readlines()
    print(lines)

    aCalA = float((lines[1])[0:6])
    bCalA = float((lines[2])[0:6])
    cCalA = float((lines[3])[0:6])

    aCalB = float((lines[4])[0:6])
    bCalB = float((lines[5])[0:6])
    cCalB = float((lines[6])[0:6])
    #avg = float(lines[4])

    calFile.close()
except Exception as e:
    #print(e)
    #print("no calibration file found, using default values")
    aCalA = 0
    bCalA = 1
    cCalA = 0

    aCalB = 0
    bCalB = 1
    cCalB = 0

#print the calibrated values from the file
print(aCalA)
print(bCalA)
print(cCalA)

print(aCalB)
print(bCalB)
print(cCalB)

global avgNum
avgNum = queue.Queue()

root = Tk()

root.geometry("600x750")

#make frames for maneagement
buttonFrame = Frame(root)
graphFrame = Frame(root)
buttonFrame.pack(side=TOP)
graphFrame.pack(side=BOTTOM)

#make entry boxes
aEntry = Entry(buttonFrame)
bEntry = Entry(buttonFrame)
aEntry.grid(row=1, column=0)
bEntry.grid(row=1, column=2)

global desiredA
global desiredB

#define functions to get last V sent and not repeat if same
global globOut
try:
    #print(globOut.get(timeout=0))
    globOut.get(timeout=0)

except:
    globOut = queue.Queue()

desiredA = queue.Queue()
desiredB = queue.Queue()

global setA
global setB

Label(buttonFrame, text="Set Desired 'A' Value").grid(row=0, column=0)
Label(buttonFrame, text="Set Desired 'B' Value").grid(row=0, column=2)

#define the graph
f = Figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)
a.set(ylim=(0, 50), xlim=(0, 25))
a.autoscale(enable=False, axis='x')
a.autoscale(enable=False, axis='y')

canvas = FigureCanvasTkAgg(f, graphFrame)
canvas.draw()
canvas.get_tk_widget().grid(row=0, column=0)

#deal with serial connection queues
try:
    #print(ser)
    test = ser
except:
    ser = serial.Serial()

global serc

try:
    #print(serc.get(timeout=0))
    serc.get(timeout=0)
except:
    serc = queue.Queue()
    serc.put(ser)

global AVals
global BVals

AVals = []
BVals = []

PortsAvailableArray = []

#make port selecter drop down

#get the current serial ports
ports = serial.tools.list_ports.comports()

#find the ports and append only the names to the dictionary
for port in sorted(ports):
    endChar = None
    selChar = 6
    while endChar == None:
        if ("{}".format(port))[selChar] == " ":
            endChar = selChar
        else:
            selChar += 1
    PortsAvailableArray.append(("{}".format(port))[0:endChar])

#port tkinter variable
serialTkvar = StringVar(root)

#set default value
try:
    serialTkvar.set(PortsAvailableArray[int(lines[0])])
except:
    pass

#make drop down and label
portsMenu = OptionMenu(buttonFrame, serialTkvar, *PortsAvailableArray)
portsMenu.grid(row=2, column=2)
Label(buttonFrame, text="Choose a port").grid(row=2, column=1)

#what happens when you change selection
def change_port(*args):
    #print( serialTkvar.get() )
    calFile = open("CalibratedValues.txt", 'w')
    for i in range(len(PortsAvailableArray) + 1):
        if PortsAvailableArray[i-1] == serialTkvar.get():
            try:
                lines[0] = (str(i-1) + "\n")
            except:
                lines = [str(i-1) + "\n"]
                #print(lines)

    #lines[0] = serialTkvar.get()
    calFile.writelines(lines)
    calFile.close()
    pass

#link dropdown to change function
serialTkvar.trace('w', change_port)

#port tkinter variable
discTkvar = StringVar(root)

#make drop down and label
discMenu = OptionMenu(buttonFrame, discTkvar, *range(10))
discMenu.grid(row=5, column=1)
Label(buttonFrame, text="Level of Discomfort").grid(row=5, column=0)

#what happens when you change selection
def change_Discomfort(*args):
    try:
        AValData.append(AVals[len(AVals)-1])
        BValData.append(AVals[len(AVals)-1])
        DiscomfortData.append(discTkvar.get())
    except Exception as e:
        print(e)
#link dropdown to change function
discTkvar.trace('w', change_Discomfort)

#make slider for the pain "levels"
painVar = StringVar(root)

painScale = Scale(buttonFrame, from_=0, to_=10, orient = 'horizontal', variable = painVar)
painScale.grid(row=1, column=5)
Label(buttonFrame, text="Set Pain Level").grid(row=0, column=5)

def start_graph():
    ser = serial.Serial(
        port = serialTkvar.get(),
        baudrate = 9600,
        timeout = 0,
        xonxoff = False,     #disable software flow control
        rtscts = True,     #disable hardware (RTS/CTS) flow control
        dsrdtr = True,       #disable hardware (DSR/DTR) flow control
        writeTimeout = 2
    )
    print("starting")
    serc.put(ser)

    if tempsChanged == False:
        desiredA.put(27)
        desiredB.put(27)
        tempsChanged = True

#program to make the numbers 4 digits

def four_dig(input):
    # convert temp into Arduino  command.
    # Arduino ranges from 0V - 0 to 5V - 4094. Every volt is 10 degrees
    if input > 49:
        input = 49
    input1 = input * 82
    input1 = str(input1)
    if (len(input1)==1):
        return "000" + input1
    elif (len(input1)==2):
        return "00" + input1
    elif (len(input1)==3):
        return "0" + input1
    elif (len(input1)==4):
        return input1
    else:
        return -1

#set default temperatures

try:
    if tempsChanged == False:
        desiredA.put(27)
        desiredB.put(27)
        tempsChanged = True
except Exception as e:
    #print(e)
    tempsChanged = True
    aEntry.delete(0, last=None)
    bEntry.delete(0, last=None)

    aEntry.insert(0, "27")
    bEntry.insert(0, "27")

    desiredA.put(27)
    desiredB.put(27)

#make start button
startButton = Button(buttonFrame, text="Start", command=start_graph)
startButton.grid(row=2, column=0)

#function to restart the restart program
def resetProgram():
    os.execl(sys.executable, sys.executable, *sys.argv)

#make reset button
resetButton = Button(buttonFrame, text="Reset", command=resetProgram)
resetButton.grid(row=3, column=1)

def setCold():
    manualTemp.get(timeout=0)
    manualTemp.put(False)

    aEntry.delete(0, "end")
    bEntry.delete(0, "end")

    aEntry.insert(0, "10")
    bEntry.insert(0, "10")

    changedA()
    changedB()

#make reset button
coldButton = Button(buttonFrame, text="Set Cold", command=setCold)
coldButton.grid(row=4, column=0)

def setHot():
    manualTemp.get(timeout=0)
    manualTemp.put(False)

    aEntry.delete(0, "end")
    bEntry.delete(0, "end")

    aEntry.insert(0, "40")
    bEntry.insert(0, "40")

    changedA()
    changedB()

#make reset button
hotButton = Button(buttonFrame, text="Set Hot", command=setHot)
hotButton.grid(row=4, column=1)

def setTG():
    manualTemp.get(timeout=0)
    manualTemp.put(True)

    aEntry.delete(0, "end")
    bEntry.delete(0, "end")

    painScale.set(7)

    changedA()
    changedB()

#make reset button
TGButton = Button(buttonFrame, text="Thermal Grill", command=setTG)
TGButton.grid(row=4, column=2)

def Save():
    filename =  filedialog.asksaveasfilename(initialdir = "",title = "Select file",filetypes = (("CSV files","*.csv"),("Text files","*.txt"),("all files","*.*")))

    with open(filename, mode='w+') as data_file:
        data_writer = csv.writer(data_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        data_writer.writerow(['A Temp', 'B Temp', 'Level of Discomfort'])

        for i in range(len(DiscomfortData)):
            print(i)
            data_writer.writerow([AValData[i], BValData[i], DiscomfortData[i]])

    print (filename)

#make reset button
SaveButton = Button(graphFrame, text="Save Data to File", command=Save)
SaveButton.grid(row=1, column=0)

#execute the calibrate script in a terminal
def Calibrate():
    #subprocess.call(["python3", "Calibrate.py"])
    os.system("python3 Calibrate.py")


#make calibrate button
calibrateButton = Button(buttonFrame, text="Calibrate", command=Calibrate)
calibrateButton.grid(row=1, column=1)

def animate(i):
    try:
        avgNum2 = avgNum.get(timeout=0)
    except Exception as e:
        #print(e)
        pass

    a.autoscale(enable=False, axis='x')
    try:
        serialConnection = serc.get(timeout=0)
        serc.put(serialConnection)
        for r in range(2):
            #get string from serial connection
            s = str(serialConnection.readline())
            #truncate to just the actual output
            x = s[2:9]
            #check to see if it's an A or B value, and append to correct dictionary
            if x[0] == 'A':
                newVal = aCalA*((float(x[2:6]))*(float(x[2:6]))) + bCalA*(float(x[2:6])) + cCalA

                if(len(AVals) >= 3):
                    newVal = ((newVal + AVals[len(AVals)-2] + AVals[len(AVals)-3] + AVals[len(AVals)-4])/4)

                AVals.append(newVal)
            elif x[0] == 'B':
                newVal = aCalB*((float(x[2:6]))*(float(x[2:6]))) + bCalB*(float(x[2:6])) + cCalB

                if(len(BVals) >= 3):
                    newVal = ((newVal + BVals[len(BVals)-2] + BVals[len(BVals)-3] + BVals[len(BVals)-4])/4)

                BVals.append(newVal)

        while not len(AVals) == len(BVals):
            #get string from serial connection
            s = str(serialConnection.readline())
            #truncate to just the actual output

            x = s[2:9]

            #check to see if it's an A or B value, and append to correct dictionary
            if x[0] == 'A':
                newVal = aCalA*((float(x[2:6]))*(float(x[2:6]))) + bCalA*(float(x[2:6])) + cCalA
                if(len(AVals) >= 3):
                    newVal = ((newVal + AVals[len(AVals)-2] + AVals[len(AVals)-3] + AVals[len(AVals)-4])/4)
                AVals.append(newVal)
            elif x[0] == 'B':
                newVal = aCalB*((float(x[2:6]))*(float(x[2:6]))) + bCalB*(float(x[2:6])) + cCalB
                if(len(BVals) >= 3):
                    newVal = ((newVal + BVals[len(BVals)-2] + BVals[len(BVals)-3] + BVals[len(BVals)-4])/4)
                BVals.append(newVal)

        a.clear()
        a.plot(AVals, "b")
        a.plot(BVals, "r")

        if(len(AVals) >= 25):
            a.xlim(len(AVals)-24, len(AVals))

        print("A:" + str(AVals[len(AVals)]))
        print("B:" + str(BVals[len(BVals)]))

    except Exception as e:
        pass
        #print()

    if len(AVals) > 49:
        a.set_xlim(left=len(AVals) - 50, right=len(AVals))
        a.set_ylim(0, 50)
    else:
        a.set_xlim(0, 50)
        a.set_ylim(0, 50)

    try:
        setB = desiredB.get(timeout=0)
        desiredB.put(setB)
    except:
        pass

    try:
        setA = desiredA.get(timeout=0)
        desiredA.put(setA)
    except:
        pass

    try:
        aOut = int(setA)
        bOut = int(setB)

        aOut = four_dig(aOut)
        bOut = four_dig(bOut)
    except:
        pass

    try:
        out = globOut.get(timeout=0)
    except Exception as e:
        #print(str(e))
        out = None

    try:
        preOut = aOut + bOut
        #print(out)

        preOut = preOut.encode('utf-8')
        #print(str(preOut) + ", " + str(out))
        if preOut == out:
            globOut.put(preOut)
        else:
            out = aOut + bOut
            out = out.encode('utf-8')
            globOut.put(out)
            print('Sending Output: ', out)
            serialConnection.write(out)
    except Exception as e:
        #print(e)
        '''
        if "out" in e:
            out = aOut + bOut
            out = out.encode('utf-8')
            #globOut.put(out)
            print('Sending Output: ', out)
        '''
#wait for someone to press enter to change the desired temperatures

def changedA(event=None):
    with desiredA.mutex:
        desiredA.queue.clear()
    desiredA.put(aEntry.get())

def changedB(event=None):
    with desiredB.mutex:
        desiredB.queue.clear()
    desiredB.put(bEntry.get())

def sliderChanged(*args):
    try:
        if manualTemp.get(timeout=0) == True:
            manualTemp.put(True)
            aEntry.delete(0, "end")
            bEntry.delete(0, "end")

            aEntry.insert(0, str(27 + int(round(float(painVar.get())*(17/10)))))
            bEntry.insert(0, str(27 - int(round(float(painVar.get())*(17/10)))))

            changedA()
            changedB()
        else:
            manualTemp.put(False)

    except Exception as e:
        #print(e)
        pass

aEntry.bind('<Return>', changedA)
bEntry.bind('<Return>', changedB)

painVar.trace('w', sliderChanged)

ani = animation.FuncAnimation(f,animate, interval=500)
root.mainloop()
