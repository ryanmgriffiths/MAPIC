from __future__ import division
import matplotlib.pyplot as plt
import numpy


data = numpy.loadtxt('datairq.txt')
hdat = numpy.average(data,axis=1)
plt.figure()
plt.hist(hdat,100,color='b')
plt.title('Am-241 Energy Spectrum')
plt.xlabel('Voltage (V)')
plt.ylabel('Counts')
#plt.yscale('log')
plt.show()