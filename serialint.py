import serial
import time
from array import array
import numpy
import matplotlib.pyplot as plt

data = numpy.zeros((1000,1000),dtype='uint8')
ser = serial.Serial('COM7', 115200,timeout=10)

for x in range(1000):
    #raw_data = ser.read_until(bytes('pos','utf-8'))
    #print(len(raw_data))
    #if len(raw_data)==2003:
    #    data[x,:] = numpy.array(array('H',raw_data[:-3]))      
    read = ser.read(2000)
    data[x,:] = numpy.frombuffer(read,dtype='uint16')
    
    
print('Done!')

datalong = data.flatten()
x = numpy.arange(len(datalong))
plt.figure()
plt.plot(x,datalong)
plt.show()


numpy.savetxt('data.txt',data)