# main.py -- put your code here!
#Import relevant modules
import network
import pyb
import utime
import machine
import micropython
import usocket as socket
from machine import Pin
from pyb import ExtInt
from pyb import USB_VCP
from pyb import I2C
from pyb import ADC
from pyb import DAC
from pyb import LED
from array import array

micropython.alloc_emergency_exception_buf(100) # For interrupt debugging

#==================================================================================#
# SETUP
#==================================================================================#

# OBJECT DEFINITIONS
led = LED(1)                            # define diagnostic LED
#usb = USB_VCP()                         # init VCP object, NOT IN USE

i2c = I2C(1, I2C.MASTER,
    baudrate=400000)                    # define I2C channel, master/slave protocol and baudrate needed
ti = pyb.Timer(2,freq=1000000)          # init timer for interrupts

# PIN SETUP AND INITIAL POLARITY/INTERRUPT MODE
Pin('PULL_SCL', Pin.OUT, value=1)       # enable 5.6kOhm X9/SCL pull-up
Pin('PULL_SDA', Pin.OUT, value=1)       # enable 5.6kOhm X10/SDA pull-up
adc = ADC(Pin('X12'), False)            # define ADC pin for pulse stretcher measurement
#calibadc = ADC(Pin('X3'))              # define ADC pin for measuring shaper voltage
pin_mode = Pin('X8', Pin.OUT)           # define pulse clearing mode pin
pin_mode.value(1)                       # low -> automatic pulse clearing, high -> manual pulse clear
clearpin = Pin('X7',Pin.OUT)            # choose pin used for manually clearing the pulse once ADC measurement is complete
polarpin = Pin('X6', Pin.OUT)           # define pin that chooses polarity   
testpulsepin = Pin('X4',Pin.OUT)        # pin to enable internal test pulses on APIC
polarpin.value(0)                       # set to 1 for positive polarity

# DATA STORAGE AND COUNTERS
sendbuf = array('H',[500])
data = array('H',[0]*4)                 # buffer for writing adc interrupt data from adc.read_timed() in calibration() and ADC_IT_poll()
calibdata = array('H',[0]*4)            # buffer to store ADC data from calibadc
count=0                                 # counter for pulses read
ratecounter = 0                         # counter for rate measurements
STATE = "STARTUP"                       # state variable for applying startup settings etc. 

# SET UP WIRELESS ACCESS POINT
wl_ap = network.WLAN(1)                 # init wlan object
wl_ap.config(essid='PYBD')              # set AP SSID
wl_ap.config(channel=1)                 # set AP channel
wl_ap.active(1)                         # enable the AP

# LOOP UNTIL A CONNECTION IS RECEIVED
while wl_ap.status('stations')==[]:
    utime.sleep(1)

# SET UP THE NETWORK SOCKET FOR UDP
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.bind(('',8080))                           # network listens on port 8080, any IP
destipv4 = ('192.168.4.16', 8080)           # destination for sending data
print("SOCKET BOUND")

#==================================================================================#
# BOARD STATE CHECKING
#==================================================================================#

def checkstate():
    a = STATE.encode('utf-8')
    s.sendto(a, destipv4)

def setstate():
    utime.sleep(0.1)
    STATE = s.recv(32).decode('utf-8')

def drain_socket():
    s.settimeout(0)
    while True:
        try:
            s.recv(2048)
        except:
            break
    s.settimeout(None)

#==================================================================================#
# I2C CONTROL
# Ir, read both I2C chips and send via socket.
# Iw, write 8 bit val to an I2C pot.
# Is, scan for the I2C addresses on the pulse stretcher.
# If the I2C chips are not connected, an exception will be raised.
#==================================================================================#

def Ir():
    if i2c.is_ready(0x2D) and i2c.is_ready(0x2C):
        gain = i2c.recv(1,addr=0x2D)
        threshold = i2c.recv(1,addr=0x2C)
        s.sendto(gain,destipv4)
        s.sendto(threshold,destipv4)
    else:
        raise Exception
    return None

def Iw(address):
    if i2c.is_ready(address):
        recvd = s.recv(1)
        value = int.from_bytes(recvd,'little',False)
        b = bytearray([0x00,value])
        i2c.send(b,addr=address)
    else:
        raise Exception
    return None

def Is():
    scan = bytearray(2)
    i2clist = i2c.scan()
    if i2clist == []:
        pass
    else:
        for idx,chip in enumerate(i2clist):
            scan[idx] = chip
    s.sendto(scan, destipv4)
    return None

#==================================================================================#
# CALIBRATION CURVE CODE FIXME: Find a way to measure this properly
#==================================================================================#
"""
def calibrate():
    global calibint
    #clearpin.value(1)
    #clearpin.value(0)
    calibint.enable()
    utime.sleep(10)
    calibint.disable()

def cbcal(line):
    #adc.read_timed(data,t2)
    s.sendto(data,destipv4)
    #clearpin.value(1)
    #clearpin.value(0)
    calibadc.read_timed(calibdata,t2)
    s.sendto(calibdata,destipv4)
"""
#==================================================================================#
# RATE MEASUREMENT CODE
#==================================================================================#

def rateaq():
    print('COUNTING RATE')
    global ratecounter
    global rateint

    ratecounter=0
    a=utime.ticks_ms()
    rateint.enable()
    utime.sleep(4)
    rateint.disable()
    
    b = utime.ticks_ms()-a
    finalrate = round((ratecounter/(b/1000)))
    finalratebyte = finalrate.to_bytes(4,'little',False)
    s.sendto(finalratebyte,destipv4)

def ratecount(line):
    global ratecounter
    ratecounter+=1
    clearpin.value(1)               # perform pulse clearing
    clearpin.value(0)

#==================================================================================#
# ADC INTERRUPT MEASUREMENT CODE:                            
# Python level legacy function, interrupt to take and send data    
# samples mnum peaks, uses schedule to delay measurements for               
# concurrent interrupts.                                
#==================================================================================#

def ADC_IT_poll():
    
    global extint
    global count
    count = 0
    
    utime.sleep(0.5)    
    msg, addr = s.recvfrom(8)
    mnum = int.from_bytes(msg,'little')
    mnum=mnum*1.2

    utime.sleep(1)
    extint.enable()
    
    while count < mnum:
        pass
    
    extint.disable()
    print("MEASUREMENT COMPLETE")
    drain_socket()

# ISR CALLBACK FUNCTION
def callback(arg):
    
    extint.disable()
    global count                    # reference the global count counter
    adc.read_timed(data,ti)         # 4 microsecond measurement from ADC at X12,
    
    pos = (4*count)%500
    
    if pos == 124:
        sendbuf[pos:pos+4] = data
        try:
            s.sendto(sendbuf, destipv4)
        except:
            print("SEND FAILED")
    else:
        sendbuf[pos:pos+4] = data

    count+=1                                # pulse counter
    extint.enable()                         # re-enable interrupts

# TEMP FIX FOR ISR OVERFLOW
# Uses micropython.schedule to delay interrupts
# that occur during ISR callback - interrupting usocket transfer is v. bad.
def cb(line):
    micropython.schedule(callback,'a')


# ENABLE GPIO INTERRUPTs
irqstate=pyb.disable_irq()                      # disable all interrupts during initialisation
rateint = ExtInt('X1', ExtInt.IRQ_RISING,
    pyb.Pin.PULL_NONE, rateaq)                  # rate measurement interrupts on pin X1
rateint.disable()

extint = ExtInt('X2',ExtInt.IRQ_RISING,
    pyb.Pin.PULL_NONE,cb)                       # interrupts for ADC pulse DAQ on pin X2
extint.disable()

pyb.enable_irq(irqstate)                        # re-enable interrupts

#==================================================================================#
# C ADC data stream method
# Wait for this to complete before attempting any other actions.
# Uses a different ADC setup from python level ADC_IT_poll.
#==================================================================================#

def read_DMA():
    msg = s.recv(4)
    mnum = int.from_bytes(msg,'little')
    mnum = mnum+1000
    adc.read_dma(mnum)

#==================================================================================#
# COMMAND CODES:
# Bytearrays used by main loop to execute functions
# expect a 2-byte command.
#==================================================================================#

commands = {
    # bytes(bytearray([a,b])) : command function,
    bytes(bytearray([0,0])) : Ir,                               # read first gain potentiometer, then threshold
    bytes(bytearray([0,2])) : Is,                               # scan I2C addresses
    bytes(bytearray([1,0])) : lambda : Iw(0x2D),                # write gain pot
    bytes(bytearray([1,1])) : lambda : Iw(0x2C),                # write threshold pot
    
    bytes(bytearray([2,0])) : read_DMA,                         # testing DMA interrupts measurements,
    bytes(bytearray([2,1])) : ADC_IT_poll,                      # legacy python ADC interrupts method
    
    bytes(bytearray([2,2])) : adc.read_interleaved,             # TODO: Implement this feature properly - requires deinit adc ability??
    
    bytes(bytearray([4,0])) : lambda : polarpin.value(0),       # Negative polarity
    bytes(bytearray([4,1])) : lambda : polarpin.value(1),       # Positive polarity

    #bytes(bytearray([5,0])) : calibrate,                       # FIXME: measure detector/apic gain profile 
    bytes(bytearray([5,1])) : rateaq,                           # measure sample rate

    bytes(bytearray([6,0])) : lambda: testpulsepin.value(0),    # disable test pulses
    bytes(bytearray([6,1])) : lambda: testpulsepin.value(1),     # enable test pulses

    bytes(bytearray([7,1])) : checkstate,                       # check the state of the pybaord
    bytes(bytearray([7,0])) : setstate,                         # set the current state of the board
}

#==================================================================================#
# MAIN LOOP
#==================================================================================#

while True:
    mode = s.recv(2)            # wait until the board receives the 2 byte command code, no timeout
    print("MODE RECEIVED")
    commands[mode]()            # reference commands dictionary and run the corresponding function