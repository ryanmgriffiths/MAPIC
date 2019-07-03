# main.py -- put your code here!
#Import relevant modules
import pyb
import time
from array import array

#measurement time constants
m_time = 0.001
freqmax = 1000000
#Diagnositcs constants
a = 0
b = 0

#Define objects
adc = pyb.ADC(pyb.Pin.board.X12)
t = pyb.Timer(1,freq=freqmax)
usb = pyb.USB_VCP()

#Wait for serial connection to open
while True:
    if usb.isconnected():
        break
    else:
        time.sleep(0.5)

#Setup variables/file/buffer
l = [0]*int(freqmax*m_time)
buf = array("H",l)
list_time = []

#Take readings
for rd in range(1):
    #a = utime.ticks_us()
    adc.read_timed(buf,t)
    usb.write(buf)
    #b = utime.ticks_us() - a
    list_time.append(b)

usb.write('end')#end condition for pyserial read.

#end flash
led1 = pyb.LED(2)
led1.on()
for x in range(15):
    led1.toggle()
    time.sleep(0.05)
