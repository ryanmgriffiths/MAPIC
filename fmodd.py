# Make a dAPIC class to add to the main code, possible to update aspects such as I2C addresses, call method to read/write/scan
# Method for ADC reads
# Tkinter works with classes?
# Modify for wifi integration too!
import serial
import socket

class APIC:
    def __init__(self, address,tout):
        self.tout = tout # Timeout
        self.address = address #COM port/or dev/tty
        self.ser = serial.Serial(address,115200,timeout=tout)
        self.reads = 0
        self.read = bytearray(2000)

    def readI2C(self,pot):
        if pot != 0 or 1:
            raise ValueError('Function only takes addresses 0, 1 for gain, width pots.')
        sercom = bytearray([0,address])
        self.ser.write(sercom)
        reply = self.ser.read(1)
        print(int.from_bytes(reply,'little'))

    def writeI2C(self,pot):
        if pot != 0 or 1:
            raise ValueError('Function only takes addresses 0, 1 for gain, width pots.')
        sercom = bytearray([1,address])
        value = int(input('value\n>'))
        self.ser.write(sercom)
        self.ser.write(bytes([value]))

    def scanI2C(self):
        sercom = bytearray([0,2])
        self.ser.write(sercom)
        time.sleep(0.5)
        if self.ser.in_waiting()>0:
            print(self.ser.readline().decode()[:-2])
        else:
            print('No I2C devices found.')

    def test(self):
        sercom = bytearray([3,3])
        self.ser.write(sercom)
        print(self.ser.read(6))
        
    def ADC_poll(self,datapoints):
        pass
    def ADC_trig(self,datapoints):
        pass
