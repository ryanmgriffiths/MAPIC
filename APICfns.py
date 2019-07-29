'''Module containing APIC Class with methods to control pyboard peripherals and the measurement protocols.'''

import serial       # USB serial communication
import socket       # Low level networking module
import datetime     # for measuring rates
import numpy
import os           # OS implementation for file saving

class APIC:
    '''Class representing the APIC. Methods invoke measurement and information 
    requests to the board and manage communication over the network socket. I.e. control the board from the PC with this class.'''
    
    def __init__(self,address,tout,ipv4):   # Intialise connection variables.
        self.tout = tout                    # Timeout for both serial and socket connections in seconds.
        self.address = address              # COM port/or dev/tty OS dependent.
        self.ipv4 = ipv4                    # Tuple of IP string and port e.g. ('123.456.78.9',1234) (see readme & socket)
        self.sock = socket.socket(socket.AF_INET
            ,socket.SOCK_STREAM)            # Init socket obj in AF_INET (IPV4 addresses only) mode and send/receive data.
        self.sock.settimeout(tout)          # Socket timeout.
        self.sock.connect(ipv4)             # Init connection to the socket.
        #self.ser = serial.Serial(address,115200,timeout=tout)          # Connect to the serial port & init serial obj.
    
        # SET FILE NUMBERS FOR DATA SAVING
        self.raw_dat_count = 0              #  counter for the number of raw data files
        


        # Find the number of relevant files currently in the data directory, select file version number.
        for datafile in os.listdir('histdata'):
            if datafile.startswith('datairq'):
                self.raw_dat_count+=1
            else:
                pass

    def createfileno(self,fncount):
        '''A function that is used to create the 4 digit file number endings based on latest version'''
        fncount=str(fncount)                        # int fncount to string 
        fnstring = list('0000')                     # convert to mutable list
        fnstring[-len(fncount):] = list(fncount)    # replace last x terms with new version        
        return ''.join(fnstring)
    
    def ps_correction(self,datarray):
            return numpy.log((datarray/0.0015))/2.0799

    def scanI2C(self):
        '''Scan for discoverable I2C addresses to the board, returning a list of found I2C addresses in decimal.'''
        sercom = bytearray([0,2])
        self.sock.send(sercom)                  # Send byte code to init scan protocol on board
        addresses = list(self.sock.recv(2))     # Recieve a list of 2 I2C addresses in list of 8 bit nums
        self.I2Caddrs = addresses
    
    def connect(self):
        '''Reconnect to the pyboard.'''
        self.sock.connect(self.ipv4)

    def readI2C(self):
        '''Read the two I2C digital potentiometers. Creates apic items posGAIN and posWIDTH which store the potentiometer 
        positions.'''
        sercom = bytearray([0,0])                                     
        self.sock.send(sercom)                                              # Send byte command.
        self.posGAIN = int.from_bytes(self.sock.recv(1),'little')           # receive gain position
        self.posWIDTH = int.from_bytes(self.sock.recv(1),'little')          # receive width position

    def testI2C(self,pot):
        '''Initiate calibration test for the potentiometers.'''
        sercom = (bytearray[5,pot])
        self.sock.send(sercom)

    def testpulses(self,value):
        '''Enable test pulses on APIC, value=1 is on, value=0 is off.'''
        sercom=bytearray([6,value])
        self.sock.send(sercom)

    def writeI2C(self,pos,pot):
        '''Writes 8 bit values to one the two digital potentiometers. One argument pot dictates which potentiometer to
        write to, the conversion of the byte command is done on the board and an actual hex address is assigned there.'''
        sercom = bytearray([1,pot])
        self.sock.send(sercom)                  # Send byte command.
        self.sock.send(bytes([pos]))          # Convert desired pot value to bytes and send.
    
    def polarity(self,polarity=1):
        '''Connection and byte transfer protocol testing. Send a byte command a receive a message back.'''
        if polarity == 0:
            sercom = bytearray([4,polarity])
            self.sock.send(sercom)
        else:
            sercom = bytearray([4,polarity])
            self.sock.send(sercom)

    def ADCi(self,datpts):
        '''Hardware interrupt routine for ADC measurement. Sends an 8 byte number for the  number of samples , 
        returns arrays of 1) 8 samples of peaks in ADC counts and times at the end of each peak in microseconds 
        from the start of the experiment.'''
        sercom = bytearray([2,1])
        
        readm = bytearray(8)               # Bytearray for receiving ADC data (with no mem allocation)
        #logtimem = bytearray(4)            # Bytearray to receive times

        self.data = numpy.zeros((datpts,4),dtype='uint16')           # ADC values numpy array
        #times = numpy.zeros(datpts,dtype='uint32')             # End of peak timestamps array
        datptsb = datpts.to_bytes(8,'little',signed=False)      # convert data to an 8 byte integer for sending
        self.sock.send(sercom)              # Send byte command
        self.sock.send(datptsb)                                 # send num if data points to sample
        
        # Read data from socket into data and times in that order, given a predictable number of bytes coming through.
        for x in range(datpts):
            self.sock.recv_into(readm,8)
            self.data[x,:] = numpy.frombuffer(readm,dtype='uint16')
            #self.sock.recv_into(logtimem,4)
            #times[x] = int.from_bytes(logtimem,'little')     

        #self.data = self.data*(3.3/4096)
        #self.data = self.ps_correction(self.data)

        # Save and return the arrays.
        numpy.savetxt('histdata\datairq'+self.createfileno(self.raw_dat_count)+'.txt',self.data)
        #numpy.savetxt('timeirq.txt',times)
