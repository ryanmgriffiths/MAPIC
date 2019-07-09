import serial
import time
from array import array
import numpy
import matplotlib.pyplot as plt
import sys
import warnings

ser = serial.Serial('COM4', 115200,timeout=10)
gain = '0x2C'
width = 0x2C

def ADC():
    readings = input('Size >')
    data = numpy.zeros((readings,1000),dtype='uint16')

    for x in range(readings):
        read = ser.read(2000)
        data[x,:] = numpy.frombuffer(read,dtype='uint16')

    return data

while True:

    cmd = bytes(input('>'),'utf-8')

    if cmd == 'I2C_r':
        
        address = address = input('gain/width:\n>')
        ser.write('I2C_r\n')
        ser.write(address+'\n')
        while ser.inwaiting() == 0:
            pass
        print(int.from_bytes(ser.readline(),'big'))
    
    elif cmd == 'I2C_w':
        
        address = input('gain/width:\n>')
        value = int(input('Value:\n>'))
        ser.write('I2C_w\n')
        ser.write(address+'\n')
        ser.write(bytes(value))

    else:
        print('Invalid command.') 
    
    print('Complete')