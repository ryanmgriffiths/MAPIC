import serial   # USB serial communication
import socket   # Low level networking module
import datetime 
import numpy    
import time

class APIC:
    '''Class representing the APIC. Methods invoke measurement and information requests to the board
    and manage communication over the network socket. I.e. control the board from the PC with this class.'''
    
    def __init__(self,address,tout,ipv4):                               # Intialise connection variables.
    self.tout = tout                                                    # Timeout for both serial and socket connections in seconds.
        self.address = address                                          # COM port/or dev/tty OS dependent.
        self.ipv4 = ipv4                                                # Tuple of IP string and port e.g. ('123.456.78.9',1234) (see readme & socket)
        #self.ser = serial.Serial(address,115200,timeout=tout)          # Connect to the serial port & init serial obj.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # Init socket obj in AF_INET (IPV4 addresses only) mode and send/receive data.
        self.sock.settimeout(tout)                                      # Socket timeout.
        self.sock.connect(ipv4)                                         # Init connection to the socket.
    
    def scanI2C(self):
        '''Scan for discoverable I2C addresses to the board, returning a list of found I2C addresses in decimal.'''
        
        sercom = bytearray([0,2])
        self.sock.send(sercom)                  # Send byte code to init scan protocol on board.
        time.sleep(0.5)
        addresses = list(self.sock.recv(2))     # Recieve a list of addresses as two 1 byte numbers, should be two I2C addresses.
        print(addresses)
        return addresses

    def readI2C(self,pot):
        '''Read one of the two I2C digital potentiometers. Takes argument pot which can be integer 0 or 1 indicating which
        pot to control. Reads value from socket and converts to an integer and returns it.'''
        
        if pot != 0 and pot != 1:                                       # Ensure only these two values are able to be passed.
            raise ValueError('Function only takes addresses 0, 1 for gain, width pots.')
        sercom = bytearray([0,pot])                                     
        self.sock.send(sercom)                                          # Send byte command.
        self.reply = self.sock.recv(1)                                  # 1 byte number from the digital pot represents current position.
        self.reply = int.from_bytes(reply,'little')                     # Convert back to an integer.
        print(self.reply)
        return self.reply

    def writeI2C(self,pot):
        '''Writes 8 bit values to one the two digital potentiometers. One argument pot dictates which potentiometer to
        write to, the conversion of the byte command is done on the board and an actual hex address is assigned there.'''
        
        if pot != 0 and pot != 1:                                       # Ensure only these two values are able to be passed.
            raise ValueError('Function only takes addresses 0, 1 for gain, width pots.')
        sercom = bytearray([1,pot])                                   
        value = int(input('value\n>'))                                  # Take a 1 byte number input for the position to write.
        self.sock.send(sercom)                                          # Send byte command.
        self.sock.send(bytes([value]))                                  # Convert desired pot value to bytes and send.

    def test(self):
        '''Connection and byte transfer protocol testing. Send a byte command a receive a message back.'''
        
        sercom = bytearray([3,3])
        self.sock.send(sercom)              # Send byte command.
        print(self.sock.recv(6))            # Receive a predicatble 6 chars over socket.

    def ADC_i(self,datpts):
        '''Hardware interrupt routine for ADC measurement. Sends an 8 byte number for the  number of samples to procure, returns arrays of 1) 8 samples
        of peaks in ADC counts and times at the end of each peak in microseconds from the start of the experiment.'''
        
        sercom = bytearray([2,1])
        self.sock.send(sercom)                                          # Send byte command.
        readm = bytearray(16)                                           # Bytearray for receiving ADC data (with no mem allocation).
        #logtimem = bytearray(4)                                         # Bytearray to receive times.
        datpts = int(input('Init?'))
        data = numpy.zeros((datpts,8),dtype='uint16')                   # ADC values numpy array.
        #times = numpy.zeros(datpts,dtype='uint32')                      # End of peak timestamps array.
        datptsb = datpts.to_bytes(8,'little',signed=False)
        self.s.send(datptsb)
        
        # Read data from socket into data and times in that order, given a predictable number of bytes coming through.
        for x in range(datpts):
            self.s.recv_into(readm,16)
            #self.s.recv_into(logtimem,4)
            data[x,:] = numpy.frombuffer(readm,dtype='uint16')
            #times[x] = int.from_bytes(logtimem,'little')     
        
        # Save numpy arrays and return the arrays.
        numpy.savetxt('datairq.txt',data)
        #numpy.savetxt('timeirq.txt',times)
        return data#,times
