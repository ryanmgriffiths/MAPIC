from tkinter import *
import tkinter.ttk as ttk
import numpy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
from array import array
import datetime
import APICfns as F

### SETUP ###
root = Tk()
root.title('APIC')
#root.wm_iconbitmap('dAPIC.bmp')

### DEFINE FRAMES ###
I2Cframe = LabelFrame(root,text='I2C Digital Potentiometer Control')
I2Cframe.grid(row=1,column=1,columnspan=6,rowspan=4)

ADCframe = LabelFrame(root,text='Measurement Tools')
ADCframe.grid(row=5,column=1,columnspan=5,rowspan=3,sticky=W)

diagnostic = LabelFrame(root,text='Diagnostic Message:')
diagnostic.grid(row=6,column=6)

### I2C TOOLS FRAME ###
def read():
    apic.readI2C()
    Ireadlabel.config(text='Gain: %i , Width: %i' % (apic.posGAIN,apic.posWIDTH))

def scan():
    apic.scanI2C()
    Iscanlabel.config(text=str(apic.I2Caddrs))

Iread = Button(I2Cframe,text='Potentiometer Values',command=read).grid(row=1,column=1)
Ireadlabel = Label(I2Cframe,text='---')
Ireadlabel.grid(row=2,column=1)

Iscan = Button(I2Cframe,text='I2C Addresses',command=scan).grid(row=3,column=1)
Iscanlabel = Label(I2Cframe,text='---',bd=10)
Iscanlabel.grid(row=4,column=1)

divide = Label(I2Cframe,text='                ').grid(row=1,column=2,rowspan=6,columnspan=2)




# WRITE 8 BIT VALUES TO POTENTIOMETERS
var0 = IntVar()

def write0():
    gain = var0.get()-1
    apic.writeI2C(gain,0)


W0B = Button(I2Cframe,text='Set Gain Value',command=write0).grid(row=1,column=4,rowspan=2)
W0S = Scale(I2Cframe,orient=HORIZONTAL,tickinterval=32,resolution=1,
    from_=1,to=256,length=300,variable=var0)
W0S.grid(row=1,column=5,rowspan=2)

var1 = IntVar()

def write1():
    width = var1.get()-1
    apic.writeI2C(width,1)

W1B = Button(I2Cframe,text='Set Width Value',command=write1).grid(row=3,column=4,rowspan=2)
W1S = Scale(I2Cframe,orient=HORIZONTAL,tickinterval=32,resolution=1,
    from_=1,to=256,length=300,variable=var1)
W1S.grid(row=3,column=5,rowspan=2)

### ADC Control Frame ###
numadc=StringVar()

def ADCi():
    datapts = int(numadc.get())
    adcidata = apic.ADCi(datapts)
    histogram = plt.Figure(dpi=100)
    global ax1
    ax1 = histogram.add_subplot(111)
    hdat = numpy.average(adcidata,axis=1)
    ax1.hist(hdat,200,(0,3100),color='b',edgecolor='black')
    ax1.set_title('Energy Spectrum')
    ax1.set_xlabel('ADC Count')
    ax1.set_.ylabel('Counts')
    plt.savefig('\histdata\histogram'+apic.raw_data_count+'.png')
    apic.raw_data_count+=1
    bar1 = FigureCanvasTkAgg(histogram, root)
    bar1.get_tk_widget().grid(row=1,column=7,columnspan=1,rowspan=10)

ADCil = Label(ADCframe, text='Interrupt Samples:')
ADCil.grid(row=1,column=1)

ADCie = Entry(ADCframe,textvariable=numadc)
ADCie.grid(row=1,column=2)

ADCout = Button(ADCframe, command=ADCi,text='Start')
ADCout.grid(row=1,column=3)

def pselect():
    apic.polarity(polarity=POL.get())

POL = IntVar()
    
divide = Label(ADCframe,text='Polarity:').grid(row=1,column=5)

# CHANGE CIRCUIT POLARITY
ppolarity = Radiobutton(ADCframe,command=pselect,text='Positive',value=1,variable=POL)
ppolarity.grid(row=2,column=5,sticky=W)
npolarity = Radiobutton(ADCframe,command=pselect,text='Negative',value=0,variable=POL)
npolarity.grid(row=3,column=5,sticky=W)

divide = Label(ADCframe,text='                   ').grid(row=1,
    column=4,rowspan=6)

### DIAGNOSTIC FRAME ###
errorbox = Message(diagnostic,text='Error messages.',
    bg='white',relief=RIDGE,width=220)
errorbox.grid(row=1,column=1)

### TOP MENU BAR ###
menubar = Menu(root)

def connect():
    '''Attempt MANUAL connection to the pyboard.'''
    try:
        apic.connect()
    except:
        errorbox.config(text='Connection failed')

def init_con():
    try:
        apic = F.APIC('COM3',10,('192.168.4.1',8080))
    except:
        errorbox.config(text='NOT CONNECTED')

# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Connect",command=connect)
filemenu.add_command(label="IP info")
filemenu.add_command(label="Disconnect")
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="Connection", menu=filemenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About")
menubar.add_cascade(label="Help", menu=helpmenu)

root.config(menu=menubar)       # display menubar
root.afer(1000, init_con)       # connect to pyboard after intitialising GUI
root.mainloop()                 # run main gui program