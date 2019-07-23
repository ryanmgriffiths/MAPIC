from tkinter import *
import numpy
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from array import array

import serial
import time
import numpy
import datetime

import APICfns as F
import matplotlib.pyplot as plt
import tkinter.ttk as ttk
import matplotlib.pyplot as plt


### SETUP ###
root = Tk()
root.title('APIC')
apic = F.APIC('COM3',10,('192.168.4.1',8080))

#root.wm_iconbitmap('dAPIC.bmp')

### DEFINE FRAMES ###
I2Cframe = LabelFrame(root,text='I2C Digital Potentiometer Control')
I2Cframe.grid(row=1,column=1,columnspan=6,rowspan=4)

ADCframe = LabelFrame(root,text='Measurement Tools')
ADCframe.grid(row=4,column=1,columnspan=5,rowspan=3,sticky=W)

diagnostic = LabelFrame(root,text='Diagnostic Message:')
diagnostic.grid(row=5,column=6)

### I2C TOOLS FRAME ###
def read():
    
    Ireadlabel.config(text='Gain: %i , Width: %i' % (g,w))

Iread = Button(I2Cframe,text='Potentiometer Values',command=read).grid(row=1,column=1)
Ireadlabel = Label(I2Cframe,text='---')
Ireadlabel.grid(row=2,column=1)

def iscan():
    apic.scanI2C()
    Iscanlabel.config(text=str(apic.I2Caddrs))

Iscan = Button(I2Cframe,text='I2C Addresses',command=iscan).grid(row=3,column=1)
Iscanlabel = Label(I2Cframe,text='---',bd=10)
Iscanlabel.grid(row=4,column=1)


# Width potentiometer
divide = Label(I2Cframe,text='                ').grid(row=1,column=2,rowspan=6,columnspan=2)

var0 = IntVar()
def write0():
    text = str(var0.get())
    W0L.config(text=text)

W0B = Button(I2Cframe,text='Set Gain Value',command=write0).grid(row=1,column=4,rowspan=2)
W0S = Scale(I2Cframe,orient=HORIZONTAL,tickinterval=32,resolution=1,
    from_=1,to=256,length=300,variable=var0)
W0S.grid(row=1,column=5,rowspan=2)
W0L = Label(I2Cframe,text='---')
W0L.grid(row=1,column=6,rowspan=2)


# Gain potentiometer
var1 = IntVar()
def write1():
    text = str(var1.get())
    W1L.config(text=text)

W1B = Button(I2Cframe,text='Set Width Value',command=write1).grid(row=3,column=4,rowspan=2)
W1S = Scale(I2Cframe,orient=HORIZONTAL,tickinterval=32,resolution=1,
    from_=1,to=256,length=300,variable=var1)
W1S.grid(row=3,column=5,rowspan=2)
W1L = Label(I2Cframe,text='---')
W1L.grid(row=3,column=6,rowspan=2)

### ADC Control Frame ###
numadc=StringVar()
def stringcontrol():
    vals = numadc.get() 
    ADCout.config(text=vals)

ADCil = Label(ADCframe, text='Interrupt Samples:')
ADCil.grid(row=1,column=1)

ADCie = Entry(ADCframe,textvariable=numadc)
ADCie.grid(row=1,column=2)

ADCout = Button(ADCframe, command=stringcontrol)
ADCout.grid(row=1,column=3)



divide = Label(ADCframe,text='Polarity:').grid(row=1,column=5)


# Polarity selector
def pselect():
    return None

ppolarity = Radiobutton(ADCframe,command=pselect,text='Positive',value=1)
ppolarity.grid(row=2,column=5,sticky=W)
npolarity = Radiobutton(ADCframe,command=pselect,text='Negative',value=2)
npolarity.grid(row=3,column=5,sticky=W)

divide = Label(ADCframe,text='                   ').grid(row=1,
    column=4,rowspan=6)


### Diagnostic Frame ###
errorbox = Message(diagnostic,text='Error 404 nothing to display here except an error that is long!',
    bg='white',relief=RIDGE,width=220)
errorbox.grid(row=1,column=1)

### Matplotlib Histogram Frame ###

histogram = plt.Figure(dpi=100)
ax1 = histogram.add_subplot(111)
ax1.plot(numpy.arange(10),numpy.arange(10))

bar1 = FigureCanvasTkAgg(histogram, root)
bar1.get_tk_widget().grid(row=1,column=7,columnspan=1,rowspan=10)
plt.close()

### Top menu bar ###
menubar = Menu(root)
# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Connect")
filemenu.add_command(label="IP info")
filemenu.add_command(label="Disconnect")
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="Connection", menu=filemenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About")
menubar.add_cascade(label="Help", menu=helpmenu)

root.config(menu=menubar)       # display menubar
root.mainloop()                 # run main gui program