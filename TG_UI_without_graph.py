from tkinter import *
import serial.tools.list_ports

#get the current serial ports
ports = serial.tools.list_ports.comports()

PortsAvailableArray = []
PortsAvailableDict = {}

#find the ports and append only the names to the dictionary
for port in sorted(ports):
    endChar = None
    selChar = 6
    while endChar == None:
        if ("{}".format(port))[selChar] == " ":
            endChar = selChar
        else:
            selChar += 1
    PortsAvailableArray.append(("{}".format(port))[1:endChar])

print(PortsAvailableArray)

root = Tk()

#make top frame/container
topFrame = Frame(root)
topFrame.pack()

#make bottom frame/container
bottomFrame = Frame(root)
bottomFrame.pack(side=BOTTOM)

#make start button
startButton = Button(topFrame, text="Start")
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

root.mainloop()
