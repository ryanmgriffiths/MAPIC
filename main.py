# main.py -- put your code here!
#Import relevant modules
import pyb
import time
from array import array

#Filtering - likely unnecessary
"""
def fltlow(element):
    return element > 1000
"""

#constants
m_time = 0.001
freqmax = 1000000
a = 0
b = 0

#Define objects
adc = pyb.ADC(pyb.Pin.board.X12)
#rtc = RTC()
t = pyb.Timer(1,freq=freqmax)
usb = pyb.USB_VCP()
time.sleep(10)
well = usb.isconnected()


#Interrupt code

"""
l = [0]*10
buf = array("H",l)


def callback(line):
    adc.read_timed(buf,t)
    print(buf)

extint = pyb.ExtInt(pyb.Pin.board.X12, pyb.ExtInt.IRQ_RISING, pyb.Pin.PULL_NONE, callback)
"""


#Setup variables/file/buffer

l = [0]*int(freqmax*m_time)
buf = array("H",l)

list_time = []

for rd in range(1):

    a = utime.ticks_us()
    adc.read_timed(buf,t)
    usb.write(buf)
    b = utime.ticks_us() - a
    list_time.append(b)


print('')

led1 = pyb.LED(2)
led1.on()
for x in range(15):
    led1.toggle()
    time.sleep(0.05)
