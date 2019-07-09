import serial
import time
from array import array
import numpy
import matplotlib.pyplot as plt

ser = serial.Serial('COM7', 115200,timeout=10)

while True:
    cmd = input('>')
    if cmd == 'Ir':
        sercom = bytearray([0,0])
        address = input('gain/width:\n>')
        
        if address == 'gain':
            address = 0
        elif address == 'width':
            address = 1
        sercom[1] = address

        ser.write(sercom)
        reply = ser.read(1)
        print(int.from_bytes(reply,'big'))

    elif cmd == 'Iw':

        sercom = bytearray([1,0])
        address = input('gain/width:\n>')
        value = int(input('value\n>'))
        
        if address == 'gain':
            address = 0
        elif address == 'width':
            address = 1
        
        sercom[1] = address
        ser.write(sercom)
        ser.write(bytes([value]))
    
    elif cmd == 'Is':
        sercom = bytearray([0,2])
        ser.write(sercom)
        print(ser.read(1))
    
    elif cmd == 'A':
        data = numpy.zeros((num_reads,1000),dtype='uint16')
        sercom = bytearray([2,0])
        reads = int(input('Readings:\n>'))
        num_reads = (reads).to_bytes(4,byteorder='big')
        ser.write(sercom)
        ser.write(num_reads)
        
        for x in range(num_reads):
            read = ser.read(2000)
            data[x,:] = numpy.frombuffer(read,dtype='uint16')
        
        numpy.savetxt('data.txt',data)
    
    else:
        print('Invalid command.')
    
    ser.reset_input_buffer()
    ser.reset_output_buffer()
