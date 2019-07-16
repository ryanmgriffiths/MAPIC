import serial
import time
from array import array
import numpy
import matplotlib.pyplot as plt
import datetime
import APICfns as F

apic = F.APIC('COM7',0.5,('192.168.4.1',8080)

while True:
    cmd = input('>')
    if cmd == 'Ir':
        potchoice = input('Gain (0) or width (1)?\n>')
        apic.readI2C(potchoice)
    elif cmd == 'Iw':
        potchoice = input('Gain (0) or width (1)?\n>')
        apic.writeI2C(potchoice)
    elif cmd == 'Is':
        apic.scanI2C()
    elif cmd == 'T':
        apic.test()
    elif cmd == 'ADi':
        datapoints = int(input('32Bit range:\n>'))
        apic.ADC_trig(datapoints)
    elif cmd == 'Ic':
        pass
    else:
        print('Invalid command.')