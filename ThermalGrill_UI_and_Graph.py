#import basic tkinter stuff
from tkinter import *
#import tool to find the serial ports
import serial.tools.list_ports
#import all the stuff for matplotlib graph
import matplotlib
#set the backend to use and import navigation bar
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
#import figure for graph
from matplotlib.figure import Figure
#import the animation library to allow for realtime updates
import matplotlib.animation as animation
#import serial to handle serial connecrtions
import serial
#make graph look better with style
from matplotlib import style
style.use("ggplot")

#get the current serial ports
ports = serial.tools.list_ports.comports()

PortsAvailableArray = []
PortsAvailableDict = {}

f = Figure(figsize=(5,5), dpi=100)
a = f.add_subplot(111)
a.set(ylim=(0, 35))

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

print(PortsAvailableArray)

root = Tk()

#make top frame/container
topFrame = Frame(root)
topFrame.pack()

#make bottom frame/container
bottomFrame = Frame(root)
bottomFrame.pack(side=BOTTOM)

#command to start the graph (right now it just makes a graph until I make the serial connections)
def start_graph():

    #a.plot([1,2,3,4,5,6,7,8],[5,6,1,3,8,9,3,5])

    canvas = FigureCanvasTkAgg(f, bottomFrame)
    canvas.draw()
    canvas.get_tk_widget().pack()
    canvas._tkcanvas.pack()


def animate(i):
    ser = serial.Serial(
        port = serialTkvar.get(),
        baudrate = 9600,
        timeout = 1,
        xonxoff = False,     #disable software flow control
        rtscts = True,     #disable hardware (RTS/CTS) flow control
        dsrdtr = True,       #disable hardware (DSR/DTR) flow control
        writeTimeout = 2
    )

    AVals = [1]
    BVals = [3]
    #get string from serial connection
    s = str(ser.readline())
    #truncate to just the actual output
    x = s[2:6]
    #check to see if it's an A or B value, and append to correct dictionary
    if x[0] == 'A':
        AVals.append(x[2:4])
    elif x[0] == 'B':
        BVals.append(x[2:4])
    print(AVals)
    #print(BVals)
    a.plot(AVals, BVals)
    #a.draw()

#make start button
startButton = Button(topFrame, text="Start", command=start_graph)
startButton.pack(side=LEFT)
        #make port selecter drop down

#port tkinter variable
serialTkvar = StringVar(root)

#set default value
serialTkvar.set(PortsAvailableArray[0])

#make drop down and label
portsMenu = OptionMenu(topFrame, serialTkvar, *PortsAvailableArray)
portsMenu.pack(side=RIGHT)
Label(topFrame, text="Choose a port").pack(side=RIGHT)

#what happens when you change selection
def change_port(*args):
    print( serialTkvar.get() )

#link dropdown to change function
serialTkvar.trace('w', change_port)

ani = animation.FuncAnimation(f, animate, interval=1000)
root.mainloop()
