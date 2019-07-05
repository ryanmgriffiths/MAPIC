import serial
import time
from array import array
import numpy
import matplotlib.pyplot as plt
import sys

ser = serial.Serial('COM4', 115200,timeout=10)

def ADC():
    readings = input('Size >')
    data = numpy.zeros((readings,1000),dtype='uint16')

    for x in range(readings):
        read = ser.read(2000)
        data[x,:] = numpy.frombuffer(read,dtype='uint16')

    return data

while True:

    cmd = bytes(input('>'),'utf-8')
    if cmd == 'ADC_r'":
        ADC()
    
    elif cmd == 'I2C_r':
        while ser.inwaiting == 0:
            pass
        print(int(ser.readline()))
    elif cmd == 'I2c_w': 
    else:
        ser.close()


