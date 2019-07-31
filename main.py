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
from array import array
from pyb import LED
micropython.alloc_emergency_exception_buf(100) # For interrupt debugging

# OBJECT DEFINITIONS
led = LED(1)                # define diagnostic LED
usb = USB_VCP()             # init VCP object
# usb.setinterrupt(-1)        # enables sending raw bytes over serial without interpreting interrupt key ctrl-c and aborting
i2c = I2C(1, I2C.MASTER,
    baudrate=400000)        # define I2C channel, master/slave protocol and baudrate needed
t2 = pyb.Timer(1,freq=1000000)          # init timer for polling
ti = pyb.Timer(2,freq=1000000)          # init timer for interrupts

# PIN SETUP AND INITIAL POLARITY/INTERRUPT MODE
#####
Pin('PULL_SCL', Pin.OUT, value=1)       # enable 5.6kOhm X9/SCL pull-up
Pin('PULL_SDA', Pin.OUT, value=1)       # enable 5.6kOhm X10/SDA pull-up
adc = ADC(Pin('X12'))                   # define ADC pin for pulse stretcher measurement
calibadc = ADC(Pin('X3'))               # define ADC pin for measuring internal test pulses
pin_mode = Pin('X8', Pin.OUT)           # define pulse clearing mode pin
pin_mode.value(0)                       # enable manual pulse clearing (i.e. pin -> high)
clearpin = Pin('X7',Pin.OUT)            # choose pin used for manually clearing the pulse once ADC measurement is complete
polarpin = Pin('X6', Pin.OUT)           # define pin that chooses polarity   
#testpulsepin = Pin('X1',Pin.OUT)        # pin to enable internal test pulses on APIC ### NOT ENABLED YET
polarpin.value(0)                       # set to 1 to achieve positive polarity

# DATA STORAGE AND COUNTERS
data = array('H',[0]*4)         # buffer for writing adc interrupt data from adc.read_timed() in calibration() and ADCi()
calibdata = array('H',[0]*4)    # buffer to store ADC data from calibadc
tim = bytearray(4)              # bytearray for microsecond, 4 byte timestamps
t0=0                            # time at the beginning of the experiment
count=0                         # counter for pulses read
ratecounter = 0

# SET UP WIRELESS ACCESS POINT
wl_ap = network.WLAN(1)                 # init wlan object
wl_ap.config(essid='PYBD')              # set AP SSID
wl_ap.config(channel=1)                 # set AP channel
wl_ap.active(1)                         # enable the AP

# SET UP THE NETWORK SOCKET
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('',8080))                       # network bound to port 8080
s.listen(1)                             # listen on this port, 1 connection tolerated
conn, addr = s.accept()                 # accept any connection
print('Connected!')                     ### diagnostic purposes only, not seen by socket

### I2C CONTROL ###
def Ir():
    if i2c.is_ready(0x2D) and i2c.is_ready(0x2C):
        gain = i2c.recv(1,addr=0x2D)
        threshold = i2c.recv(1,addr=0x2C)
        conn.send(gain)
        conn.send(threshold)
    else:
        raise Exception
    return None

def Iw(address):
    if i2c.is_ready(address):
        value = int.from_bytes(conn.recv(1),'little')
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
    conn.send(scan)
    return None


### CALIBRATION CURVE CODE ###

def calibrate():
    global calibint
    calibint.enable()
    clearpin.value(1)
    clearpin.value(0)
    utime.sleep(10)
    calibint.disable()

def cbcal(line):
    adc.read_timed(data,t2)
    conn.send(calibdata)
    clearpin.value(1)
    clearpin.value(0)
    calibadc.read_timed(calibdata)

### SOURCE RATE COUNTER ###
def rateaq():
    print('started')
    clearpin.value(1)               # perform pulse clearing
    clearpin.value(0)
    global ratecounter
    global rateint
    ratecounter=0
    a=utime.ticks_ms()
    rateint.enable()
    utime.sleep(3)
    rateint.disable()
    b = utime.ticks_ms()-a
    finalrate = round((ratecounter/(b/1000)))
    finalratebyte = finalrate.to_bytes(4,'little',False)
    conn.send(finalratebyte)

def ratecount(line):
    global ratecounter
    ratecounter+=1
    clearpin.value(1)               # perform pulse clearing
    clearpin.value(0)
    print(ratecounter)

### ADC INTERRUPT MEASUREMENT CODE ###

# MAIN ADC MEASUREMENT CODE
def ADCi():
    a=utime.ticks_ms()
    clearpin.value(1)
    clearpin.value(0)
    global extint
    global count
    count = 0
    mnum = int.from_bytes(conn.recv(8),'little')
    #t0 = int(utime.ticks_us())
    extint.enable()
    while count < mnum:
        pass
    extint.disable()
    extint = None
    b = utime.ticks_ms()-a
    print(mnum/(b/1000))

# ISR CALLBACK FUNCTION
def callback(arg):
    irqstate = pyb.disable_irq()
    adc.read_timed(data,ti)         # 4 microsecond measurement from ADC at X12,
    global count                    # reference the global count counter
#    tim[:] = (int(utime.ticks_us() - t0)).to_bytes(4,'little')     # timestamp the pulse
#    conn.send(tim)                 # send timestamp over socket
    conn.send(data)                 # send adc sample over socket
    clearpin.value(1)               # perform pulse clearing
    clearpin.value(0)
    count+=1                 # pulse counter
    pyb.enable_irq(irqstate)

# TEMP FIX FOR ISR OVERFLOW
# Uses micropython.schedule to delay interrupts
# that occur during callback.
def cb(line):
    micropython.schedule(callback,'a')

# ENABLE INTERRUPT CHANNELS
irqstate=pyb.disable_irq()                  # disable all interrupts during initialisation
calibint = ExtInt('X1',ExtInt.IRQ_RISING,
    pyb.Pin.PULL_NONE,cbcal)                # calibration routine interrupts on pin X1
extint = ExtInt('X2',ExtInt.IRQ_RISING,
    pyb.Pin.PULL_NONE,cb)                   # interrupts for ADC pulse DAQ on pin X2
rateint = ExtInt('X4',ExtInt.IRQ_RISING,
    pyb.Pin.PULL_NONE,ratecount)            # interrupts to measure sample activity on pin X4

# disable each individually using extint for later enabling in the functions
extint.disable()
calibint.disable()
rateint.disable()
pyb.enable_irq(irqstate) # re-enable irqs

#irq = Pin('X2').irq(handler=cb,trigger=Pin.IRQ_RISING,priority=10, wake=None, hard=True)
# COMMAND CODES: bytearrays that the main program uses to execute functions above/simple
# functions that are defined in the dict
commands = {
# bytes(bytearray([])) : ,
    bytes(bytearray([0,0])) : Ir,    # read first gain potentiometer, then threshold

    bytes(bytearray([0,2])) : Is,                       # scan I2C
    bytes(bytearray([1,0])) : lambda : Iw(0x2D),        # write gain pot
    bytes(bytearray([1,1])) : lambda : Iw(0x2C),        # write threshold pot
    bytes(bytearray([2,1])) : ADCi,                     # ADC interrupts

    bytes(bytearray([4,0])) : lambda : polarpin.value(0),       # Negative polarity
    bytes(bytearray([4,1])) : lambda : polarpin.value(1),       # Positive polarity

    bytes(bytearray([5,0])) : calibrate,           # measure detector/apic gain profile 
    bytes(bytearray([5,1])) : rateaq,              # measure sample rate

    bytes(bytearray([6,0])) : lambda: testpulsepin.value(0),    # disable test pulses
    bytes(bytearray([6,1])) : lambda: testpulsepin.value(1)     # enable test pulses
}

# MAIN PROGRAM LOOP
while True:
    mode = conn.recv(2)         # wait until the board receives the 2 byte command code, no timeout
    commands[mode]()            # reference commands dictionary and run the corresponding function
