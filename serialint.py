import serial
import time
from array import array
import numpy
import matplotlib.pyplot as plt
import sys

readings = 1000
data = numpy.zeros((readings,1000),dtype='uint16')
ser = serial.Serial('COM7', 115200,timeout=10)
'''a = array('L',[readings])
ser.write(a)
print(sys.getsizeof(a))
'''
a = time.time()

for x in range(readings):
    read = ser.read(2000)
    #data[x,:] = numpy.frombuffer(read,dtype='uint16')

b = time.time()
print('Done!',b-a)

datalong = data.flatten()
x = numpy.arange(len(datalong))

plt.figure()
plt.plot(x,datalong)
plt.show()


numpy.savetxt('data.txt',data)

