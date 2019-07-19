# main.py -- put your code here!
#Import relevant modules
import network
import utime
import usocket as socket
from machine import Pin
from pyb import ExtInt
from pyb import USB_VCP
from pyb import I2C
from pyb import ADC
from array import array
from pyb import LED


# OBJECT DEFINITIONS
led = LED(1)                # define diagnostic LED
usb = USB_VCP()             # init VCP object
usb.setinterrupt(-1)        # enables sending raw bytes over serial without interpreting interrupt key ctrl-c and aborting
i2c = I2C(1, I2C.MASTER,
    baudrate=400000)        # define I2C channel, master/slave protocol and baudrate needed
adc = ADC(Pin('X12'))                   # define ADC pin
pin_mode = Pin('X8', Pin.OUT)           # define pulse clearing mode pin
pin_mode.value(1)                       # enable manual pulse clearing (i.e. pin -> high)
clearpin = Pin('X7',Pin.OUT)            # choose pin used for manually clearing the pulse once ADC measurement is complete
Pin('PULL_SCL', Pin.OUT, value=1)       # enable 5.6kOhm X9/SCL pull-up
Pin('PULL_SDA', Pin.OUT, value=1)       # enable 5.6kOhm X10/SDA pull-up
tp = pyb.Timer(1,freq=1000000)          # init timer for polling
ti = pyb.Timer(2,freq=2000000)          # init timer for interrupts

# DATA STORAGE AND COUNTERS
data = array('H',[0]*8)     # buffer into which ADC readings are written to avoid memory allocation
tim = bytearray(4)          # bytearray for microsecond, 4 byte timestamps
t0=0                        # time at the beginning of the experiment
const=0                     # counter for pulses read


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


### SETUP SUCCESS - DIAGNOSTIC ONLY
for x in range(10):
    led.toggle()
    utime.sleep_ms(100)
    led.toggle()

# OPERATION FUNCTIONS
def Ir(address):
    if i2c.is_ready(address):
        recv = i2c.recv(1,addr=address)
        conn.send(recv)
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

def ADCp():
    n_reads = int.from_bytes(conn.recv(4),'little')
    buf = array("H",[0]*2048)
    for term in range(n_reads):
        adc.read_timed(buf,tp)
        conn.send(buf)
    return None

def ADCi():
    global const
    const = 0
    extint.enable()
    mnum = int.from_bytes(conn.recv(8),'little')
    #t0 = int(utime.ticks_us())
    while const < mnum:
        pass
    extint.disable()

### DIAGNOSTIC FUNCTION
def test():
    buf = bytes('Hello!','utf-8')
    conn.send(buf)
    conn.send(buf)
    return None

# INTERRUPT CALLBACK FUNCTION
def callback(line):
    adc.read_timed(data,ti)         # 4 microsecond measurement from ADC at X12,
    global const                    # reference the global const counter
#    tim[:] = (int(utime.ticks_us() - t0)).to_bytes(4,'little')     # timestamp the pulse
#    conn.send(tim)                 # send timestamp over socket
    conn.send(data)                 # send adc sample over socket
    clearpin.value(1)               # perform pulse clearing
    clearpin.value(0)
    const = const+1                 # pulse counter                                                                



# COMMAND CODES: bytearrays that the main program looks for to execute functions above.
commands = {
    bytes(bytearray([0,0])) : lambda : Ir(0x2C),    # read gain pot
    bytes(bytearray([0,1])) : lambda : Ir(0x2D),    # read width pot
    bytes(bytearray([0,2])) : Is,                   # scan I2C
    bytes(bytearray([1,0])) : lambda : Iw(0x2C),    # write gain pot
    bytes(bytearray([1,1])) : lambda : Iw(0x2D),    # write width pot
    bytes(bytearray([2,0])) : ADCp,                 # ADC polling
    bytes(bytearray([2,1])) : ADCi,                 # ADC interrupts
    bytes(bytearray([3,3])) : test,                 # communication test
}

extint = ExtInt('X1',ExtInt.IRQ_RISING,
    pyb.Pin.PULL_NONE,callback)     # init hardware irq on pin X1, rising edge and executes function callback
extint.disable()                    # immediately disable interrupt to ensure it doesnt fill socket buffer

# MAIN PROGRAM LOOP
while True:
    mode = conn.recv(2)         # wait until the board receives the 2 byte command code, no timeout
    commands[mode]()            # reference dictionary and run the corresponding function