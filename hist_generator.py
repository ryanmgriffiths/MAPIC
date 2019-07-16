from __future__ import division
import numpy
import matplotlib.pyplot as plt

raw_data = numpy.loadtxt('datawifi.txt')
rmsvals = []
flatdata = raw_data.flatten()
flatx = numpy.arange(len(flatdata))

plt.figure()
plt.plot(flatx,flatdata)
plt.show()
plt.close()

selected = numpy.where(flatdata > 250)[0]
print(selected)
print(len(selected))
c = 0

for idx, x in enumerate(selected):
    try:
        if selected[idx + 1] ==  x + 1:
            c = c + 1 
        else:
            sliced = flatdata[selected[idx-c]:selected[idx]]
            print(sliced)
            rmsval = numpy.sqrt(numpy.average(sliced**2))
            print(rmsval)
            rmsvals.append(rmsval)
            c=0
    except:
        print('exception!')

plt.figure()
plt.hist(1.8*(numpy.array(rmsvals)/4096),50)
plt.ylabel('Frequency')
plt.xlabel('Voltage (V)')
plt.savefig('histogram.png')
plt.show()
plt.close()