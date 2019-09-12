from gekko import GEKKO
import numpy as np
import sys
import serial
import serial.tools.list_ports
import time
from tkinter import *

root = Tk()

root.geometry("600x400")

#make or edit config file
f = open("CalibratedValues.txt","r+")

lines = f.readlines()
print(lines)

f.close()

ports = serial.tools.list_ports.comports()

PortsAvailable = []
PortsAvailablePrintable = []

for port in sorted(ports):
    endChar = None
    selChar = 8
    while endChar == None:
        if ("{}".format(port))[selChar] == " ":
            endChar = selChar
        else:
            selChar += 1

    PortsAvailable.append(("{}".format(port))[0:endChar])

selPort = 0

for port in sorted(ports):
    PortsAvailablePrintable.append(str(selPort) + ': ' + PortsAvailable[selPort])
    selPort += 1

print(PortsAvailablePrintable)

root.grid_columnconfigure(2, weight=1)

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(3, weight=1)
root.grid_rowconfigure(6, weight=1)
root.grid_rowconfigure(9, weight=1)

                        #A Temps
#Labels
Label(root, text="A Temps").grid(row=0, column=1)
Label(root, text="Sent Temp").grid(row=1, column=0)
Label(root, text="Actual Temp").grid(row=2, column=0)
Label(root, text="Sent Temp").grid(row=4, column=0)
Label(root, text="Actual Temp").grid(row=5, column=0)
Label(root, text="Sent Temp").grid(row=7, column=0)
Label(root, text="Actual Temp").grid(row=8, column=0)
Label(root, text="Sent Temp").grid(row=10, column=0)
Label(root, text="Actual Temp").grid(row=11, column=0)
#Entrys
xVal1AEntry = Entry().grid(row=1, column=1)
xVal2AEntry = Entry().grid(row=4, column=1)
xVal3AEntry = Entry().grid(row=7, column=1)
xVal4AEntry = Entry().grid(row=10, column=1)

yVal1AEntry = Entry().grid(row=2, column=1)
yVal2AEntry = Entry().grid(row=5, column=1)
yVal3AEntry = Entry().grid(row=8, column=1)
yVal4AEntry = Entry().grid(row=11, column=1)

                        #B Temps
#Labels
Label(root, text="B Temps").grid(row=0, column=4)
Label(root, text="Sent Temp").grid(row=1, column=3)
Label(root, text="Actual Temp").grid(row=2, column=3)
Label(root, text="Sent Temp").grid(row=4, column=3)
Label(root, text="Actual Temp").grid(row=5, column=3)
Label(root, text="Sent Temp").grid(row=7, column=3)
Label(root, text="Actual Temp").grid(row=8, column=3)
Label(root, text="Sent Temp").grid(row=10, column=3)
Label(root, text="Actual Temp").grid(row=11, column=3)
#Entrys
xVal1BEntry = Entry().grid(row=1, column=4)
xVal2BEntry = Entry().grid(row=4, column=4)
xVal3BEntry = Entry().grid(row=7, column=4)
xVal4BEntry = Entry().grid(row=10, column=4)

yVal1BEntry = Entry().grid(row=2, column=4)
yVal2BEntry = Entry().grid(row=5, column=4)
yVal3BEntry = Entry().grid(row=8, column=4)
yVal4BEntry = Entry().grid(row=11, column=4)

f = open("CalibratedValues.txt","w+")

connectingPortID = input("Please type the number of the port you would like to use: ")
connectingPort = PortsAvailable[int(connectingPortID)]
#write the wanted port to the config file
try:
    lines[0] = (str(connectingPortID) + "\n")
except:
    print("port exception")
    lines = [(str(connectingPortID) + "\n")]

yVal1A = input('Please manually set to new temperature, then input what is displayed on device after stabilization: ')
xVal1A = input('Type what is being sent over serial: ')

yVal2A = input('Please manually set to new temperature, then input what is displayed on device after stabilization: ')
xVal2A = input('Type what is being sent over serial: ')

yVal3A = input('Please manually set to new temperature, then input what is displayed on device after stabilization: ')
xVal3A = input('Type what is being sent over serial: ')

yVal4A = input('Please manually set to new temperature, then input what is displayed on device after stabilization: ')
xVal4A = input('Type what is being sent over serial: ')

ymA = np.array([yVal1A, yVal2A, yVal3A, yVal4A])
xmA = np.array([xVal1A, xVal2A, xVal3A, xVal4A])

print(xmA)

A = GEKKO()

x = A.Param(value=xmA)

a = A.FV()
b = A.FV()
c = A.FV()

a.STATUS = 1
b.STATUS = 1
c.STATUS = 1

y = A.CV(value=ymA)
y.FSTATUS = 1

A.Equation(y==a*(x*x) + b*x + c)

A.options.IMODE = 2

A.solve(disp=False)

print(a.Value[0])
print(b.Value[0])
print(c.Value[0])
#write the equation vars to config file


try:
    lines[1] = (str(a.Value[0]) + "\n")
    lines[2] = (str(b.Value[0]) + "\n")
    lines[3] = (str(c.Value[0]) + "\n")

except Exception as e:
    print(e)
    lines.append(str(a.Value[0]) + "\n")
    lines.append(str(b.Value[0]) + "\n")
    lines.append(str(c.Value[0]) + "\n")
    '''
    f.write(str(a.Value[0]) + "\n")
    f.write(str(b.Value[0]) + "\n")
    f.write(str(c.Value[0]) + "\n")
'''
f.writelines(lines)
f.close()

