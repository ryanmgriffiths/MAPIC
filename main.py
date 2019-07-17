# main.py -- put your code here!
#Import relevant modules
import usocket as socket
import network
from pyb import USB_VCP
from pyb import I2C
from pyb import ADC
from array import array
from pyb import LED
import utime
from machine import Pin

# OBJECT DEFINITIONS
led = LED(1)
usb = USB_VCP()
usb.setinterrupt(-1)
i2c = I2C(1, I2C.MASTER,baudrate=400000)
adc = ADC(Pin('X12'))
pin_i =  Pin('X1', Pin.IN)
Pin('PULL_SCL', Pin.OUT, value=1)       # enable 5.6kOhm X9/SCL pull-up
Pin('PULL_SDA', Pin.OUT, value=1)       # enable 5.6kOhm X10/SDA pull-up
tp = pyb.Timer(1,freq=1000000)          # timer for polling
ti = pyb.Timer(2,freq=2000000)          # timer for interrupts
const=0
data = array('H',[0]*8)
tim = bytearray(4)
t0 = 0


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

# SETUP SUCCESS
for x in range(50):
    led.toggle()
    utime.sleep_ms(20)
    led.toggle()

"""def zsupp(buff):
    if buff > 800:
        return True
    else:
        return False"""

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
    scan = bytearray(1)
    if i2c.scan() != []:
        scan[0] = i2c.scan()[0]
    else:
        pass
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
    mnum = int.from_bytes(conn.recv(4),'little')
    t0 = int(utime.ticks_us())
    pin_i.irq(handler=callback,trigger=Pin.IRQ_RISING)
    while const < mnum:
        pass
    const = 0
    return None

def test():
    buf = bytes('Hello!','utf-8')
    conn.send(buf)
    conn.send(buf)
    return None

# INTERRUPT CALLBACK FUNCTION
def callback(line):
    global const
    adc.read_timed(data,ti)
    tim[:] = (int(utime.ticks_us() - t0)).to_bytes(4,'little')
    conn.send(data)
    conn.send(tim)
    const = const+1

# COMMAND CODES
commands = {
    bytes(bytearray([0,0])) : lambda : Ir(0x2C), # Read gain pot
    bytes(bytearray([0,1])) : lambda : Ir(0x2D), # Read width pot
    bytes(bytearray([0,2])) : Is,                # Scan I2C
    bytes(bytearray([1,0])) : lambda : Iw(0x2C), # Write gain pot
    bytes(bytearray([1,1])) : lambda : Iw(0x2D), # Write width pot
    bytes(bytearray([2,0])) : ADCp,              # ADC polling
    bytes(bytearray([2,1])) : ADCi,              # ADC interrupts
    bytes(bytearray([3,3])) : test,              # communication test
}

# MAIN PROGRAM
while True:
    mode = conn.recv(2)
    commands[mode]()
