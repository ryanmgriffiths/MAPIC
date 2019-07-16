# Make a dAPIC class to add to the main code, possible to update aspects such as I2C addresses, call method to read/write/scan
# Method for ADC reads
# Tkinter works with classes?
# Modify for wifi integration too!
import serial
import socket
import datetime
import numpy

class APIC:
    def __init__(self, address,tout,ipv4):
        self.tout = tout # Timeout
        self.address = address #COM port/or dev/tty
        self.ipv4 = ipv4
        self.ser = serial.Serial(address,115200,timeout=tout)
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect(ipv4)

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

    def ADC_trig(self,datpts):
        data = numpy.zeros((datpts,8),dtype='uint16')
        times = numpy.zeros(datpts,dtype='uint32')  
        datptsb = datpts.to_bytes(8,'little',signed=False)
        d0 = datetime.datetime.now()
        self.s.send(datptsb)
        
        for x in range(datpts):
            self.s.recv_into(readm,16)
            self.s.recv_into(logtimem,4)
            data[x,:] = numpy.frombuffer(readm,dtype='uint16')
            times[x] = int.from_bytes(logtimem,'little')

        d1 = datetime.datetime.now()

        numpy.savetxt('datairq.txt',data)
        numpy.savetxt('timeirq.txt',times)

        d = d1-d0
        d = d.total_seconds()
        print(d)
