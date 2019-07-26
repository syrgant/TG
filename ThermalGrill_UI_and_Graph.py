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

f = Figure(figsize=(10,8), dpi=100)
a = f.add_subplot(111)
a.set(ylim=(0, 50), xlim=(0, 25))
a.autoscale(enable=False, axis='x')

canvas = FigureCanvasTkAgg(f, root)
canvas.draw()
canvas.get_tk_widget().pack()

try:
    print(ser)
except:
    ser = serial.Serial()

global serc

try:
    print(serc.get(timeout=1))
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
#serialTkvar.set(PortsAvailableArray[0])

#make drop down and label
portsMenu = OptionMenu(root, serialTkvar, *PortsAvailableArray)
portsMenu.pack(side=RIGHT)
Label(text="Choose a port").pack(side=RIGHT)

#what happens when you change selection
def change_port(*args):
    print( serialTkvar.get() )

#link dropdown to change function
serialTkvar.trace('w', change_port)


def start_graph():
    ser = serial.Serial(
        port = serialTkvar.get(),
        baudrate = 9600,
        timeout = 1,
        xonxoff = False,     #disable software flow control
        rtscts = True,     #disable hardware (RTS/CTS) flow control
        dsrdtr = True,       #disable hardware (DSR/DTR) flow control
        writeTimeout = 2
    )
    print("starting")
    serc.put(ser)

#make start button
startButton = Button(text="Start", command=start_graph)
startButton.pack(side=LEFT)

def animate(i):
    a.autoscale(enable=False, axis='x')
    try:
        serialConnection = serc.get(timeout=1)
        serc.put(serialConnection)
        for x in range(2):
            #get string from serial connection
            s = str(serialConnection.readline())
            #truncate to just the actual output
            x = s[2:6]
            #check to see if it's an A or B value, and append to correct dictionary
            if x[0] == 'A':
                AVals.append(float(x[2:6]))
            elif x[0] == 'B':
                BVals.append(float(x[2:6]))

        while not len(AVals) == len(BVals):
            #get string from serial connection
            s = str(serialConnection.readline())
            #truncate to just the actual output
            x = s[2:6]
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


ani = animation.FuncAnimation(f,animate, interval=200)
root.mainloop()

