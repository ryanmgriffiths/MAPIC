# main.py -- put your code here!
#Import relevant modules
import pyb
import time
from array import array
import utime

usb = pyb.USB_VCP()

while True:
    

    if mode == 'ADC_read':
        freqmax = 1000000
        t = pyb.Timer(1,freq=freqmax)

        #Successful connection
        '''
        readings = usb.recv(4,timeout=5000)
        readings = array('L',readings)
        '''

        readings=1000
        led.toggle()

        #Setup variables/file/buffer
        buf = array("H",[0]*1000)

        #Take readings
        for x in range(readings):
            adc.read_timed(buf,t)
            usb.write(buf)

    elif mode == 'I2C_change':
        if:
        
        elif:

            i2c = pyb.I2C(1, I2C.MASTER,baudrate=400000)

            b = bytearray([0x00,255])

    elif mode == 'I2C_read':
        
        i2c = pyb.I2C(1, I2C.MASTER,baudrate=400000)




    else:
        pass




    