# main.py -- put your code here!
#Import relevant modules

from pyb import USB_VCP
from pyb import I2C
from pyb import ADC
from array import array
from pyb import LED
import time
from machine import Pin

led = LED(1)
usb = USB_VCP()
i2c = I2C(1, I2C.MASTER,baudrate=400000)
adc = ADC(Pin('X12'))
Pin('PULL_SCL', Pin.OUT, value=1) # enable 5.6kOhm X9/SCL pull-up
Pin('PULL_SDA', Pin.OUT, value=1) # enable 5.6kOhm X10/SDA pull-up

# Command Codes
Ir0 = bytearray([0,0]) #Read gain pot
Ir1 = bytearray([0,1]) #Read width pot
Is = bytearray([0,2]) #Relay I2C scan
Iw0 = bytearray([1,0]) #Write gain pot
Iw1 = bytearray([1,1]) #Write width pot
A = bytearray([2,0]) #ADC polling

# Error Codes

def zsupp(buff):
    if buff > 800:
        return True
    else:
        return False

def Ir(address):
    if i2c.is_ready(address):
        recv = i2c.recv(1,addr=address)
        usb.write(recv)
    else:
        pass
    return None

def Iw(address):
    if i2c.is_ready(address):
        value = int.from_bytes(usb.recv(1,timeout=60000),'little')
        b = bytearray([0x00,value])
        i2c.send(b,addr=address)
    else:
        pass
    return None

def Is():
    scan = bytearray(1)
    if i2c.scan() != []:
        scan[0] = i2c.scan()[0]
    else:
        pass
    usb.write(scan)
    return None

def ADC():
    t = pyb.Timer(1,freq=1000000)
    n_reads = int.from_bytes(usb.recv(4,timeout=1000),'little')
    buf = array("H",[0]*1000)
    for x in range(n_reads):
        adc.read_timed(buf,t)
        usb.write(buf)#filter(zsupp,buf))
    return None

while True:

    mode = usb.recv(2,timeout=60000)
    #led.toggle()
    
    if mode==Ir0:
        Ir(0x2C)
    elif mode==Ir1:
        Ir(0x2B)
    elif mode==Is:
        Is()
    elif mode==Iw0:
        Iw(0x2C)
    elif mode == Iw0:
        Iw(0x2B)
    elif mode == A:
        ADC()
    else:
        pass
    #led.toggle()
