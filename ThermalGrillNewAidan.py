import serial
import time
import datetime
import serial.tools.list_ports
from tkinter import *
import _thread
import matplotlib.pyplot as plt

def Start():
    global ser
    ser = serial.Serial(
        port = "/dev/ttyACM0",
        baudrate = 9600,
        timeout = 1,
        xonxoff = False,     #disable software flow control
        rtscts = True,     #disable hardware (RTS/CTS) flow control
        dsrdtr = True,       #disable hardware (DSR/DTR) flow control
        writeTimeout = 2
    )

    global AVals
    global BVals

    AVals = []
    BVals = []

    plt.axis([0,50,0,50])
    plt.ylabel('Temperature')
    plt.ion()
    plt.show()

def GetVals():
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
    print(BVals)

def MakeGui(ALength, BLength):
    if ALength == -1:
        plt.plot([], [])
    else:
        plt.plot([ALength], [AVals[ALength]], 'rs', [BLength], [BVals[BLength]], 'b^')
    plt.axis([ALength-50,ALength,0,30])
    plt.draw()
    plt.pause(0.001)

def main():
    Start()
    try:
        while True:
            ALength = len(AVals) - 1
            if not ALength >= 0:
                ALength = -1
            BLength = len(BVals) - 1
            if not BLength >= 0:
                BLength = -1
            GetVals()
            MakeGui(ALength, BLength)
            time.sleep(0.25)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
