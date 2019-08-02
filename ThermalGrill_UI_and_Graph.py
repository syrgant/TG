import serial
import time
import datetime
import serial.tools.list_ports
from tkinter import *
import _thread
import matplotlib.animation as animation
import matplotlib
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

root = Tk()

root.geometry("600x600")

#make frames for maneagement
buttonFrame = Frame(root)
graphFrame = Frame(root)
buttonFrame.pack(side=TOP)
graphFrame.pack(side=BOTTOM)

aEntry = Entry(buttonFrame)
bEntry = Entry(buttonFrame)
aEntry.grid(row=1, column=0)
bEntry.grid(row=1, column=3)

global desiredA
global desiredB

desiredA = queue.Queue()
desiredB = queue.Queue()

global setA
global setB

Label(buttonFrame, text="Set Desired 'A' Value").grid(row=0, column=0)
Label(buttonFrame, text="Set Desired 'B' Value").grid(row=0, column=3)

f = Figure(figsize=(10,8), dpi=100)
a = f.add_subplot(111)
a.set(ylim=(0, 50), xlim=(0, 25))
a.autoscale(enable=False, axis='x')

canvas = FigureCanvasTkAgg(f, graphFrame)
canvas.draw()
canvas.get_tk_widget().pack()

try:
    print(ser)
except:
    ser = serial.Serial()

global serc

try:
    print(serc.get(timeout=0))
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
    serialTkvar.set(PortsAvailableArray[0])
except:
    pass

#make drop down and label
portsMenu = OptionMenu(buttonFrame, serialTkvar, *PortsAvailableArray)
portsMenu.grid(row=2, column=2)
Label(buttonFrame, text="Choose a port").grid(row=2, column=1)

#what happens when you change selection
def change_port(*args):
    print( serialTkvar.get() )

#link dropdown to change function
serialTkvar.trace('w', change_port)


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

#make start button
startButton = Button(buttonFrame, text="Start", command=start_graph)
startButton.grid(row=2, column=0)

def animate(i):
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
                AVals.append(float(x[2:6]))
            elif x[0] == 'B':
                BVals.append(float(x[2:6]))

        while not len(AVals) == len(BVals):
            #get string from serial connection
            s = str(serialConnection.readline())
            #truncate to just the actual output

            x = s[2:9]

            #check to see if it's an A or B value, and append to correct dictionary
            if x[0] == 'A':
                AVals.append(float(x[2:6]))
            elif x[0] == 'B':
                BVals.append(float(x[2:6]))

        a.clear()
        a.plot(AVals, "b")
        a.plot(BVals, "r")

        if len(AVals) > 39:
            a.set(xlim=(len(AVals) - 40, len(AVals)))
        else:
            a.set(xlim=(0, 40))
    except:
        pass

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
        aOut = float(setA)
        bOut = float(setB)

        aOut = four_dig(aOut)
        bOut = four_dig(bOut)

        out = str(aOut) + str(bOut)
        out = out.encode('utf-8')
        print('Sending Output: ', out)
    except Exception as e:
        print(e)
#wait for someone to press enter to change the desired temperatures

def changedA(event=None):
    with desiredA.mutex:
        desiredA.queue.clear()
    desiredA.put(aEntry.get())

def changedB(event=None):
    with desiredB.mutex:
        desiredB.queue.clear()
    desiredB.put(bEntry.get())

aEntry.bind('<Return>', changedA)
bEntry.bind('<Return>', changedB)

ani = animation.FuncAnimation(f,animate, interval=500)
root.mainloop()
