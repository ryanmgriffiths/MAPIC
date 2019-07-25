import serial       # USB serial communication
import socket       # Low level networking module
import datetime     # for measuring rates
import numpy
import time
import os

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

        # SET FILE NUMBERS FOR DATA SAVING
        self.raw_dat_count = 0              #  counter for the number of raw data files
        self.hist_count = 0                 #  counter for the number of histogram graphs
        
        # Find the number of files currently in the data directory.
        for datafile in os.listdir('histdata'):
            if datafile.startswith('histogram'):
                self.hist_count+=1
            elif datafile.startswith('datairq'):
                self.raw_dat_count+=1

        #self.ser = serial.Serial(address,115200,timeout=tout)          # Connect to the serial port & init serial obj.
    
    def createfileno(self,fncount,DATA):
        '''A function that is used to create the file number endings.'''
        fnstring = '0000'
        fnstring[-len(str(fncount)):] = str(fncount)
        if data==True:
            self.raw_dat_count+=1
        else:
            self.hist_count+=1
        return fnstring

    def scanI2C(self):
        '''Scan for discoverable I2C addresses to the board, returning a list of found I2C addresses in decimal.'''
        
        sercom = bytearray([0,2])
        self.sock.send(sercom)                  # Send byte code to init scan protocol on board
        time.sleep(0.5)
        addresses = list(self.sock.recv(2))     # Recieve a list of 2 I2C addresses in list of 8 bit nums
        self.I2Caddrs = addresses
    
    def connect(self):
        self.sock.connect(self.ipv4)

    def readI2C(self):
        '''Read the two I2C digital potentiometers. Creates apic items posGAIN and posWIDTH which store the potentiometer positions.'''
        sercom = bytearray([0,0])                                     
        self.sock.send(sercom)                                              # Send byte command.
        self.posGAIN = int.from_bytes(self.sock.recv(1),'little')           # receive gain position
        self.posWIDTH = int.from_bytes(self.sock.recv(1),'little')          # receive width position

    def writeI2C(self,pos,pot):
        '''Writes 8 bit values to one the two digital potentiometers. One argument pot dictates which potentiometer to
        write to, the conversion of the byte command is done on the board and an actual hex address is assigned there.'''
        sercom = bytearray([1,pot])
        self.sock.send(sercom)                  # Send byte command.
        self.sock.send(bytes([pos]))          # Convert desired pot value to bytes and send.

    def test(self):
        '''Connection and byte transfer protocol testing. Send a byte command a receive a message back.'''
        
        sercom = bytearray([3,3])
        self.sock.send(sercom)              # Send byte command.
        print(self.sock.recv(6))            # Receive a predicatble 6 chars over socket.

    def ADCi(self,datpts):
        '''Hardware interrupt routine for ADC measurement. Sends an 8 byte number for the  number of samples to procure, 
        returns arrays of 1) 8 samples of peaks in ADC counts and times at the end of each peak in microseconds 
        from the start of the experiment.'''
        sercom = bytearray([2,1])
        self.sock.send(sercom)              # Send byte command
        
        readm = bytearray(16)               # Bytearray for receiving ADC data (with no mem allocation)
        #logtimem = bytearray(4)            # Bytearray to receive times

        data = numpy.zeros((datpts,8),dtype='uint16')           # ADC values numpy array
        #times = numpy.zeros(datpts,dtype='uint32')             # End of peak timestamps array
        datptsb = datpts.to_bytes(8,'little',signed=False)      # convert data to an 8 byte integer for sending
        self.sock.send(datptsb)                                 # send num if data points to sample
        
        # Read data from socket into data and times in that order, given a predictable number of bytes coming through.
        for x in range(datpts):
            self.sock.recv_into(readm,16)
            data[x,:] = numpy.frombuffer(readm,dtype='uint16')
            print(x)
            #self.sock.recv_into(logtimem,4)
            #times[x] = int.from_bytes(logtimem,'little')     

        # Save and return the arrays.
        numpy.savetxt('datairq'+self.createfileno(self.raw_dat_count)+'.txt',data)
        self.raw_dat_count += 1
        #numpy.savetxt('timeirq.txt',times)
        return data             #,times
