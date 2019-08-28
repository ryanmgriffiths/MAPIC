'''Module containing APIC Class with methods to control pyboard peripherals and the measurement protocols.'''

import serial       # USB serial communication
import socket       # Low level networking module
import datetime     # for measuring rates
import numpy
import os           # OS implementation for file saving
import json
from array import array
from tkinter import *
import tkinter.ttk as ttk
import time
import matplotlib.pyplot as plt

fp = open("MAPICconfig.json","r")            # open the json config file in rw mode
default = json.load(fp)                     # load default settings dictionary
fp.close()

class APIC:
    '''Class representing the APIC. Methods invoke measurement and information 
    requests to the board and manage communication over the network socket. I.e. control the board from the PC with this class.'''
    def __init__(self,tout,ipv4):   # intialise connection variables.
        
        self.tout = tout                            # timeout for both serial and socket connections in seconds.
        self.ipv4 = tuple(ipv4)                     # tuple of IP string and port e.g. ('123.456.78.9',1234) (see readme & socket)
        
        # SOCKET OPERATIONS
        self.sock = socket.socket(socket.AF_INET
            ,socket.SOCK_DGRAM)                     # init socket obj in AF_INET (IPV4 addresses only) mode and send/receive data.
        self.sock.settimeout(tout)                  # set socket timeout setting
        self.sock.bind(('',8080))
        self.polarity = default['polarity']

        # DATA STORAGE AND VARIABLES
        self.raw_dat_count = 0                      #  counter for the number of raw data files
        self.calibgradient = default['calibgradient']
        self.caliboffset = default['caliboffset']
        self.samples = 100
        self.savemode = default['savemode']
        self.STATE = ""
        self.errorstatus = ""
        self.units = default['units']
        self.hdat = numpy.array([])
        self.title = default['title']
        self.posGAIN = default['gainpos']
        self.posTHRESH = default['threshpos']
        self.boundaries = tuple(default['boundaries'])
        self.bins = default['bins']
        self.ylabel = ""
        self.xlabel = ""

        # Find the number of relevant files currently in the data directory, select file version number.
        for datafile in os.listdir('histdata'):
            if datafile.startswith('datairq'):
                self.raw_dat_count+=1
            else:
                pass
        
        #self.ser = serial.Serial(address,115200,timeout=tout)          # connect to the serial port & init serial obj (legacy behaviour)

    def createfileno(self,fncount):
        '''A function that is used to create the 4 digit file number endings based on latest version'''
        
        fncount=str(fncount)                        # int fncount to string
        fnstring = list('0000')                     # convert to mutable list
        fnstring[-len(fncount):] = list(fncount)    # replace last x terms with new version
        
        return ''.join(fnstring)
    
    def drain_socket(self):
        '''Empty socket of any interrupt overflow data, call after every instance of interrupt usage.\n
        Reset timeout to 10s after each call.'''
        self.sock.settimeout(0)     # set timeout 0
        
        while True:
            try:
                self.sock.recv(2048)   # read 2 byte chunks until none left -> timeout
            except:
                break               # when sock.recv timeout break loop
        
        self.sock.settimeout(default['timeout'])

    def sendcmd(self,a,b):
        '''Send a bytearray command using two 8 bit unsigned integers a,b.\n
        self.sendcmd(a,b)\n
        Arguments:\n
        \t a: first command byte for type of command \n
        \t b: second command byte for subsection.'''
        self.sock.sendto(bytearray([a,b]),self.ipv4)

    #===================================================================================================
    # STATE OPERATIONS - CURRENTLY UNUSED BUT MAY BE USEFUL
    #===================================================================================================
    
    def checkstate(self):
        
        self.sendcmd(7,0)
        print(self.sock.recv(32).decode('utf-8'))
                           
    def sendstate(self, statestr):
        
        if isinstance(statestr,str):    
            self.sendcmd(7,1)
            self.sock.sendto(statestr.encode('utf-8'),self.ipv4)
            self.STATE = statestr
        
        else:
            self.errorstatus = "ERROR: Expected String"

    def disconnect(self):
        ''' Disconnect the socket.'''
        self.sock.close()
    
    #===================================================================================================
    # I2C OPERATIONS
    #===================================================================================================
    
    def scanI2C(self):
        '''Scan for discoverable I2C addresses to the board, returning a list of found I2C addresses in decimal.\n
        Takes no arguments but stores received addresses as a list object self.I2Caddrs.'''
        
        self.sendcmd(0,2)
        addresses = list(self.sock.recv(2))     # recieve a list of 2 I2C addresses in list of 8 bit nums
        self.I2Caddrs = addresses

    def readI2C(self):
        '''Read the two I2C digital potentiometers.\n 
        Creates two APIC variables self.posGAIN, self.posTHRESH storing the positions.'''
        
        self.sendcmd(0,0)
        self.posGAIN = int.from_bytes(self.sock.recv(1),'little')           # receive + update gain position variable
        self.posTHRESH = int.from_bytes(self.sock.recv(1),'little')          # receive + update threhold position variable
    
    def writeI2C(self,pos,pot):
        '''Writes 8 bit values to one the two digital potentiometers.\n 
        self.writeI2C(pos,pot)\n 
        Arguments:
            \t pos: desired position of pot 8 bit value
            \t pot: takes value 0,1 for threshold and gain pots respectively'''
        
        self.sendcmd(1,pot)
        time.sleep(0.5)
        self.sock.sendto(bytearray([pos]),self.ipv4)

    def setpolarity(self,setpolarity=1):
        '''Connection and byte transfer protocol testing. Send a byte command a receive a message back.'''
        
        self.sendcmd(4,setpolarity)
        self.polarity= setpolarity
    
    def setunits(self,data,_units):
        if self.units == _units:
            return data
        elif self.units != _units and _units == 'mV':
            self.units = 'mV'
            return data*(3300/4096)
        elif self.units != _units and _units == 'ADU':
            self.units = 'ADU'
            return data/(3300/4096)

    def curvecorrect(self, Input):
        return ((Input + self.caliboffset)/self.calibgradient)

    def rateaq(self):
        '''Acquire measured sample activity in Bq, does not work for activities lower than 1Bq.\n
        Returns the sample rate in Hz.'''
        
        self.drain_socket()
        self.sendcmd(5,1)

        rateinb = self.sock.recv(32)
        rate = int.from_bytes(rateinb,'little',signed=False)
        
        return rate
    
    def shapergain(self,shapeV):
        '''Turns voltage data from the shaper and converts it into gains using the exponential fit. Returns the gain of the shaper.\n
        self.shapergain(shapeV)\n\n
        \t shapeV: voltage data (numpy array type) from the shaper.'''
        shapergain = 0.0375*numpy.exp(4.4156*shapeV)
        
        return shapergain

    def calibration(self):
        '''Perform a calibration of the setup, arbitrary time and creates two items of the APIC class
        containing the data received.'''
        
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

        self.outputpulses = self.setunits(numpy.array(self.outputpulses),'mV')
        self.inputpulses = self.setunits(numpy.array(self.inputpulses), 'mV')
    
    #===================================================================================================
    # ADC DAQ OPERATIONS
    #===================================================================================================
    
    def ADCi(self,datpts,progbar,rootwin):
        '''Hardware interrupt routine for ADC measurement. Sends an 8 byte number for the  number of samples,\n 
        returns arrays of 1) 8 samples of peaks in ADC counts and times at the end of each peak in microseconds\n
        from the start of the experiment.\n
        self.ADCi(datpts,progbar,rootwin)\n
        \t datpts: 64bit number for desired number of ADC samples\n
        \t progbar: progressbar widget variable\n
        \t rootwin: tkinter.TK() object (root frame/window object)'''
        
        tick_count = 0
        self.samples = datpts                                   # update samples item
        print(datpts)
        progbar['maximum'] = int((4*datpts)/500)                    # update progress bar max value
        rootwin.update_idletasks()                              # force tkinter to refresh
        
        readm = array("H",[0]*500)                              # Bytearray for receiving ADC data (with no mem allocation)
        self.data = array("H",[])                               # ADC values numpy array
        datptsb = datpts.to_bytes(8,'little',signed=False)      # convert data to an 8 byte integer for sending

        print(self.sock.gettimeout())
        self.sendcmd(2,1)
        time.sleep(0.5)                                         # Send byte command
        self.sock.sendto(datptsb,self.ipv4)                     # send num if data points to sample
        
        # Read data from socket into data and times in that order, given a predictable number of bytes coming through.
        while int(len(self.data)/4) < datpts:
            
            self.sock.recv_into(readm)
            tick_count+=1
            self.data.extend(readm)
            progbar['value'] = tick_count                       # update the progress bar value
            rootwin.update()                                    # force tkinter to update - non-ideal solution
        
        self.drain_socket()
        # Save and return the arrays.
        self.data = numpy.array(self.data)
        self.data.shape = (int(len(self.data)/4), 4)
        self.data = self.curvecorrect(self.data)                # apply linear fit corrections
    
    def savedata(self,data):
        ''' Save numpy data. '''
        print(self.raw_dat_count)
        numpy.savetxt('histdata\datairq'+self.createfileno(self.raw_dat_count)+'.txt',data)
        self.raw_dat_count+=1                               # new file version number

    def udp_test(self):
        '''INIT NEW SOCKET & TAKE DATA FROM BOARD, EXPECTS 32BIT VALUES FROM DMA BUFFER'''
        sock1 = socket.socket(socket.AF_INET
            ,socket.SOCK_DGRAM)                                 # reinit socket object
        sock1.settimeout(10)                                     # set timeout -> default this
        sock1.bind(('', 9000))
        datastore = array("L",[])                                    # ADC values numpy array
        readm = array("L",[0]*300)

        self.sendcmd(2,0)
        for x in range(100000):
            try:
                sock1.recv_into(readm)
                datastore.extend(readm)
                print(readm)
            except:
                break
        plt.figure()

        plt.plot(numpy.arange(len(datastore)),numpy.array(datastore))
        plt.xticks([])
        plt.show()
        sock1.close()