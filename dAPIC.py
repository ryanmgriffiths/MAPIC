import serial
import time
from array import array
import numpy
import matplotlib.pyplot as plt
import datetime

ser = serial.Serial('COM7', 115200,timeout=0.5)

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
        print(int.from_bytes(reply,'little'))

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

        reads = int(input('Readings:\n>'))
        breads = reads.to_bytes(4,'little',signed=False)
        data = numpy.zeros((reads,1000),dtype='uint16')
        
        sercom = bytearray([2,0])
        read = bytearray(2000)
        ser.write(sercom)
        ser.write(breads)

        for x in range(reads):
            ser.readinto(read)
            data[x,:] = numpy.frombuffer(read,dtype='uint16')
        else:
            print('Successful datalogging!')
        

        plt.figure()
        
        datalong = data.flatten()
        x = numpy.arange(len(datalong))
        plt.plot(x,datalong)
        
        plt.show()

        numpy.savetxt('data.txt',data)

    elif cmd == 'AD':
        reads = 1000
        data = numpy.zeros((reads,1000),dtype='uint16')
        sercom = bytearray([2,1])
        read = bytearray(2000)
        ser.write(sercom)
        d0 = datetime.datetime.now()


        for x in range(reads):
            ser.readinto(read)
            data[:] = numpy.frombuffer(read,dtype='uint16')
        
        d1 = datetime.datetime.now()
        d = d1-d0
        d = d.total_seconds()
        print(d)

    elif cmd == 'Ic':
        pass
    elif cmd == 'R':
        ser = serial.Serial('COM7', 115200,timeout=0.5)
    else:
        print('Invalid command.')
    
    ser.reset_input_buffer()
    ser.reset_output_buffer()