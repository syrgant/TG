from gekko import GEKKO
import numpy as np
import sys
import serial
import serial.tools.list_ports
import time

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

connectingPortID = input("Please type the number of the port you would like to use: ")
connectingPort = PortsAvailable[int(connectingPortID)]

ser = serial.Serial(
    port = connectingPort,
    baudrate = 9600,
    timeout = 0,
    xonxoff = False,     #disable software flow control
    rtscts = True,     #disable hardware (RTS/CTS) flow control
    dsrdtr = True,       #disable hardware (DSR/DTR) flow control
    writeTimeout = 2
)

xm = np.array([])

yVal1 = input('Please manually set to new temperature, then input what is displayed on device after stabilization: ')
ser.flushInput()
time.sleep(0.5)
foundVal = False
while foundVal == False:
    s = str(ser.readline())
    #truncate to just the actual output
    x = s[2:9]
    #check to see if it's an A or B value, and append to correct dictionary
    if x[0] == 'A':
        np.append(xm, float(x[2:6]))
        foundVal = True
    elif x[0] == 'B':
        foundVal = False

yVal2 = input('Please manually set to new temperature, then input what is displayed on device after stabilization: ')
ser.flushInput()
time.sleep(0.5)
foundVal = False
while foundVal == False:
    s = str(ser.readline())
    #truncate to just the actual output
    x = s[2:9]
    #check to see if it's an A or B value, and append to correct dictionary
    if x[0] == 'A':
        np.append(xm, float(x[2:6]))
        foundVal = True
    elif x[0] == 'B':
        foundVal = False

yVal3 = input('Please manually set to new temperature, then input what is displayed on device after stabilization: ')
ser.flushInput()
time.sleep(0.5)
foundVal = False
while foundVal == False:
    s = str(ser.readline())
    #truncate to just the actual output
    x = s[2:9]
    #check to see if it's an A or B value, and append to correct dictionary
    if x[0] == 'A':
        np.append(xm, float(x[2:6]))
        foundVal = True
    elif x[0] == 'B':
        foundVal = False

yVal4 = input('Please manually set to new temperature, then input what is displayed on device after stabilization: ')
ser.flushInput()
time.sleep(0.5)
foundVal = False
while foundVal == False:
    s = str(ser.readline())
    #truncate to just the actual output
    x = s[2:9]
    #check to see if it's an A or B value, and append to correct dictionary
    if x[0] == 'A':
        np.append(xm, float(x[2:6]))
        foundVal = True
    elif x[0] == 'B':
        foundVal = False


print(xm)

ym = np.array([yVal1, yVal2, yVal3, yVal4])

m = GEKKO()

x = m.Param(value=xm)

a = m.FV()
b = m.FV()
c = m.FV()

a.STATUS = 1
b.STATUS = 1
c.STATUS = 1

y = m.CV(value=ym)
y.FSTATUS = 1

m.Equation(y==a*(x*x) + b*x + c)

m.options.IMODE = 2

m.solve(disp=False)

print(a.Value[0])
print(b.Value[0])
print(c.Value[0])

f = open("CalibratedValues.txt","w+")

f.write(str(a.Value[0]) + "\n")
f.write(str(b.Value[0]) + "\n")
f.write(str(c.Value[0]) + "\n")
