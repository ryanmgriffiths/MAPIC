# main.py -- put your code here!
# main.py -- put your code here!
#Import relevant modules
import pyb
from pyb import LED
import time
from array import array
from pyb import RTC
from pyb import ADC
from pyb import Timer
import ujson
from pyb import USB_VCP
import utime

#Test pyboard function
led = LED(4)
led1 = LED(2)
led.on()
time.sleep(1)
led.off()

#Filtering
#def fltlow(element):
#    return element > 1000


#constants
m_time = 0.001
freqmax = 1000000
a = 0
b = 0

#Define objects
#comm = USB_VCP()
adc = ADC(pyb.Pin.board.X12)
rtc = RTC()
t = Timer(1,freq=freqmax)
usb = pyb.USB_VCP()

time.sleep(10)
well = usb.isconnected()
"""
l = [0]*10
buf = array("H",l)


def callback(line):
    adc.read_timed(buf,t)
    print(buf)
"""
#extint = pyb.ExtInt(pyb.Pin.board.X12, pyb.ExtInt.IRQ_RISING, pyb.Pin.PULL_NONE, callback)



#Setup variables/file/buffer
#file = open('/sd/adcdata.json','w')

l = [0]*int(freqmax*m_time)
buf = array("H",l)
#A = rtc.datetime()
"""



for read in range(10):
    t1 = Timer(10,prescaler=999,period=0xffff)
    a = t1.counter()
    adc.read_timed(buff,t)
    file.write(ujson.dumps(buff) + '\n')
    b = t1.counter()
    print(a,b)
    #buff2 = [x for x in buff if x > 1000] 
    #= (value for value in buff if value >1000)
    #buff2 = list(filter(fltlow,buff))
    
    #a = t1.counter()
    #b = t1.counter()
    #file2.write(a + ' ' + b + '\n')



B = rtc.datetime()
file.close()


ss = B[-1] - A[-1]
s = B[-2] - A[-2]
m = B[-3] - A[-3]

diff = s*256 - A[-1] + (255-B[-1])
"""
list_time = []

for rd in range(1):

    #t1 = Timer(10,prescaler=999,period=0xffff)
    a = utime.ticks_us()
    adc.read_timed(buf,t)
    #print(buf)
    usb.write(buf)
    b = utime.ticks_us() - a
    list_time.append(b)

"""
time.sleep(10)

t_dat = array('H', [243,234,1243,154,56,3563])
print(ujson.dumps(t_dat))
"""

print(list_time)

led1.on()
for x in range(15):
    led1.toggle()
    time.sleep(0.05)