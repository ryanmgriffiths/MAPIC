from __future__ import division
import numpy
import matplotlib.pyplot as plt

raw_data = numpy.loadtxt('datawifi.txt')
rmsvals = numpy.array([])
flatdata = numpy.flatten(raw_data)


sliced = numpy.array([])

for idx,x in enumerate(flatdata):
    
    if x > 200 and x not in sliced:
        del sliced[:]
        start = idx
        val = x
        numpy.append(sliced,val)
        v = 1
        
        while val > 200:
            numpy.append(sliced,flatdata[idx+v])
            v = v + 1
        
        rmsval = numpy.sqrt(numpy.average(sliced**2))
        numpy.append(rmsvals,rmsval)
    
    elif x > 200 and x in sliced:
        pass
    
    else:
        pass

plt.figure()
plt.hist(x,20)
plt.show()
plt.savefig('histogram.png')
