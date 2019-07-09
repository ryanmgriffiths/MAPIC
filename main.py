# main.py -- put your code here!
#Import relevant modules

from pyb import USB_VCP
from pyb import I2C
from pyb import ADC
from array import array

usb = USB_VCP()

while True:

    while usb.any() == False:
        pass
    mode = usb.readline().decode('utf-8')

    if mode == 'I2C_w': # Write to I2C chips

        address = usb.readline().decode('utf-8')
        value = int.from_bytes(usb.readline())
        i2c = I2C(1, I2C.MASTER,baudrate=400000)
        
        if address == 'gain':
            address = 0x2C
            b = bytearray([0x00,value])
            i2c.send(b,addr=address)

        elif address == 'width':
            pass
            
        else:
            pass

    elif mode == 'I2C_r': # Read from I2C chips
        address = usb.readline().decode('utf-8')
        i2c = I2C(1, I2C.MASTER,baudrate=400000)    

        if address == 'gain':
            address = 0x2C
            recv = i2c.recv(1,addr=0x2C)
            usb.write(recv)
        
        elif address == 'width':
            pass
            
        else:
            pass

    else:
        pass

# ADC TEST CODE, INTERRUPTS OR POLLING HERE.

""" 
    if mode == 'ADC_read':    
        
        t = pyb.Timer(1,freq=1000000)
        readings=1000
        led.toggle()

        #Setup variables/file/buffer
        buf = array("H",[0]*1000)

        #Take readings
        for x in range(readings):
            adc.read_timed(buf,t)
            usb.write(buf)
"""