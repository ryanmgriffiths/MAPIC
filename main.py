# main.py -- put your code here!
#Import relevant modules
import pyb
import time
from array import array
import utime

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
led = pyb.LED(1)

#Wait for serial connection to open
while True:
    if usb.isconnected():
        break
    else:
        time.sleep(0.5)

#Successful connection
led.toggle()
time.sleep(0.5)
led.toggle()

#Setup variables/file/buffer
l = [0]*int(freqmax*m_time)
buf = array("H",l)
s1 = 'end'
endbuff = bytes('end','utf-8')

#list_time = []



#Take readings
for x in range(1000):
    adc.read_timed(buf,t)
    usb.write(buf)
    #usb.write(bytes('pos','utf-8'))
    time.sleep(0.01)
    #b = utime.ticks_us() - a

#usb.write(endbuff)#end condition for pyserial read.


#end flash
led1 = pyb.LED(2)
led1.on()
for x in range(15):
    led1.toggle()
    time.sleep(0.05)
