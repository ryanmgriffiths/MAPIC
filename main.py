# main.py -- put your code here!
#Import relevant modules

from pyb import USB_VCP
from pyb import I2C
from pyb import ADC
from array import array
from pyb import LED
import time
from machine import Pin

# Object definitions
led = LED(1)
usb = USB_VCP()
i2c = I2C(1, I2C.MASTER,baudrate=400000)
adc = ADC(Pin('X12'))
Pin('PULL_SCL', Pin.OUT, value=1) # enable 5.6kOhm X9/SCL pull-up
Pin('PULL_SDA', Pin.OUT, value=1) # enable 5.6kOhm X10/SDA pull-up
t = pyb.Timer(1,freq=1000000)
usb.setinterrupt(-1)

"""def zsupp(buff):
    if buff > 800:
        return True
    else:
        return False"""

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
    n_reads = int.from_bytes(usb.recv(4,timeout=1000),'little')
    buf = array("H",[0]*1000)
    for term in range(n_reads):
        adc.read_timed(buf,t)
        usb.write(buf)
    return None

def test():
    buf = bytes('Hello!','utf-8')
    usb.write(buf)
    return None

# Command Codes
commands = {
    bytes(bytearray([0,0])) : lambda : Ir(0x2C), # Read gain pot
    bytes(bytearray([0,1])) : lambda : Ir(0x2B), # Read width pot
    bytes(bytearray([0,2])) : Is,                # Scan I2C
    bytes(bytearray([1,0])) : lambda : Iw(0x2C), # Write gain pot
    bytes(bytearray([1,1])) : lambda : Iw(0x2B), # Write width pot
    bytes(bytearray([2,0])) : ADCp,              # ADC polling
    bytes(bytearray([2,0])) : ADCi,              # ADC interrupts
    bytes(bytearray([3,3])) : test,              # communication test
}

while True:
    mode = usb.recv(2,timeout=60000)
    commands[mode]()