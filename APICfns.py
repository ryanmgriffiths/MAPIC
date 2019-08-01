'''Module containing APIC Class with methods to control pyboard peripherals and the measurement protocols.'''

import serial       # USB serial communication
import socket       # Low level networking module
import datetime     # for measuring rates
import numpy
import os           # OS implementation for file saving
from tkinter import *
import tkinter.ttk as ttk

class APIC:
    '''Class representing the APIC. Methods invoke measurement and information 
    requests to the board and manage communication over the network socket. I.e. control the board from the PC with this class.'''
    def __init__(self,address,tout,ipv4):   # intialise connection variables.
        self.tout = tout                    # timeout for both serial and socket connections in seconds.
        self.address = address              # COM port/or dev/tty OS dependent.
        self.ipv4 = ipv4                    # tuple of IP string and port e.g. ('123.456.78.9',1234) (see readme & socket)
        self.sock = socket.socket(socket.AF_INET
            ,socket.SOCK_STREAM)            # init socket obj in AF_INET (IPV4 addresses only) mode and send/receive data.
        self.sock.settimeout(tout)          # set socket timeout setting
        #self.sock.connect(ipv4)             # Init connection to the socket.
        self.samples=100
        
        # SET FILE NUMBERS FOR DATA SAVING
        self.raw_dat_count = 0              #  counter for the number of raw data files
        self.gradient = 0
        self.offset = 0
        
        # Find the number of relevant files currently in the data directory, select file version number.
        for datafile in os.listdir('histdata'):
            if datafile.startswith('datairq'):
                self.raw_dat_count+=1
            else:
                pass
        
        #self.ser = serial.Serial(address,115200,timeout=tout)          # connect to the serial port & init serial obj.

    def createfileno(self,fncount):
        '''A function that is used to create the 4 digit file number endings based on latest version'''
        fncount=str(fncount)                        # int fncount to string 
        fnstring = list('0000')                     # convert to mutable list
        fnstring[-len(fncount):] = list(fncount)    # replace last x terms with new version        
        return ''.join(fnstring)
    
    def drain_socket(self):
        '''Empty socket of any interrupt overflow data, call after every instance of interrupt usage.\n
        Warning: Reset timeout to default timeout after each call.'''
        self.sock.settimeout(0)     # set timeout 0
        while True:
            try:
                self.sock.recv(2)   # read 2 byte chunks until none left -> timeout
            except:
                break               # when sock.recv timeout break loop
        
    def sendcmd(self,a,b):
        '''Send a bytearray command using two 8 bit unsigned integers a,b.\n
        self.sendcmd(a,b)\n
        Arguments:\n
        \t a: first command byte for type of command \n
        \t b: second command byte for subsection.'''
        self.sock.send(bytearray([a,b]))

    def scanI2C(self):
        '''Scan for discoverable I2C addresses to the board, returning a list of found I2C addresses in decimal.\n
        Takes no arguments but stores received addresses as a list object self.I2Caddrs.'''
        self.sendcmd(0,2)
        addresses = list(self.sock.recv(2))     # recieve a list of 2 I2C addresses in list of 8 bit nums
        self.I2Caddrs = addresses
    
    def connect(self):
        '''Reconnect to the pyboard.'''
        self.sock.connect(self.ipv4)

    def readI2C(self):
        '''Read the two I2C digital potentiometers. \n Creates two APIC variables self.posGAIN, self.posWIDTH storing the positions.'''
        self.sendcmd(0,0)
        self.posGAIN = int.from_bytes(self.sock.recv(1),'little')           # receive + update gain position variable
        self.posWIDTH = int.from_bytes(self.sock.recv(1),'little')          # receive + update threhold position variable
    def writeI2C(self,pos,pot):
        '''Writes 8 bit values to one the two digital potentiometers.\n 
        self.writeI2C(pos,pot)\n 
        Arguments:
            \t pos: desired position of pot 8 bit value
            \t pot: takes value 0,1 for threshold and gain pots respectively'''
        self.sendcmd(1,pot)
        self.sock.send(bytes([pos]))          # Convert desired pot value to bytes and send.

    ### NOT ENABLED YET ###
    def testpulses(self,value):
        '''Enable test pulses on APIC, value=1 is on, value=0 is off.'''
        self.sendcmd(6,value)

    def polarity(self,polarity=1):
        '''Connection and byte transfer protocol testing. Send a byte command a receive a message back.'''
        self.sendcmd(4,polarity)
           
    def mV(self, adc_counts):
        '''Convert ADC counts to millivolts, takes ADC count data array ot single value.'''
        return adc_counts*(3300/4096)
    
    def curvecorrect(self, Input):
        return (Input/self.gradient) + self.offset

    def rateaq(self):
        '''Acquire measured sample activity in Bq, does not work for activities lower than 1Bq.'''
        self.sock.settimeout(10)
        self.sendcmd(5,1)
        rateinb = self.sock.recv(4)
        rate = int.from_bytes(rateinb,'little',signed=False)
        return rate
    
    def shapergain(self,shapeV):
        '''Turns voltage data from the shaper and converts it into gains using the exponential fit.\n
        self.shapergain(shapeV)\n
        \t shapeV: voltage data (numpy array type) from the shaper.'''
        shapergain = 0.0375*numpy.exp(4.4156*shapeV)
        return shapergain

    def calibration(self):
        '''Perform a calibration of the setup, arbitrary time and creates two items of the APIC class
        containing the data received.'''
        # send byte command code
        self.sendcmd(5,0)

        readout = bytearray(8)
        readin = bytearray(8)
        
        # define lists to append input/output data to
        self.outputpulses = []
        self.inputpulses = []

        # while loop to take data from the ADC until a timeout
        while True:
            try:
                self.sock.recv_into(readout)
                self.sock.recv_into(readin)
                self.outputpulses.append(numpy.average(numpy.frombuffer(readout,dtype='unint16')))
                self.inputpulses.append(numpy.average(numpy.frombuffer(readin,dtype='unint16')))
            except:
                print('Socket timeout!')
                break

        self.outputpulses = self.mV(numpy.array(self.outputpulses))
        self.inputpulses = self.mV(numpy.array(self.inputpulses))

    def ADCi(self,datpts,progbar,rootwin):
        '''Hardware interrupt routine for ADC measurement. Sends an 8 byte number for the  number of samples , 
        returns arrays of 1) 8 samples of peaks in ADC counts and times at the end of each peak in microseconds 
        from the start of the experiment.'''
        self.samples = datpts               # update samples item
        progbar['maximum'] = datpts         # update progress bar max value
        rootwin.update_idletasks()          # force tkinter to refresh
        readm = bytearray(8)                # Bytearray for receiving ADC data (with no mem allocation)
        #logtimem = bytearray(4)            # Bytearray to receive times

        self.data = numpy.zeros((datpts,4),dtype='uint16')      # ADC values numpy array
        #times = numpy.zeros(datpts,dtype='uint32')             # End of peak timestamps array
        datptsb = datpts.to_bytes(8,'little',signed=False)      # convert data to an 8 byte integer for sending
        self.sendcmd(2,1)                                       # Send byte command
        self.sock.send(datptsb)                                     # send num if data points to sample

        # Read data from socket into data and times in that order, given a predictable number of bytes coming through.
        for x in range(datpts):
            self.sock.recv_into(readm)
            self.data[x,:] = numpy.frombuffer(readm,dtype='uint16')
            progbar['value'] = x                                # update the progress bar value
            rootwin.update_idletasks()                          # force tkinter to update - non-ideal solution
            #self.sock.recv_into(logtimem,4)
            #times[x] = int.from_bytes(logtimem,'little')
        
        # Save and return the arrays.
        self.data = self.mV(self.data)                          # convert to millivolts
        self.data = self.curvecorrect(self.data)                # apply linear fit corrections
        numpy.savetxt('histdata\datairq'+self.createfileno(self.raw_dat_count)+'.txt',self.data)
        #numpy.savetxt('timeirq.txt',times)