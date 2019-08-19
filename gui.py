from tkinter import *
import tkinter.ttk as ttk
import numpy
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import serial
import time
from array import array
import datetime
import APICfns as F
import json

#==================================================================================#
# SETUP
# Reload previous setup from json file,
# create new apic object, connect + setup class variables for socket connection.
# init root window
# setup each frame with a label and allocate sizes with grid.
#==================================================================================#

fp = open("APICconfig.json","r")            # load config file in rw mode
default = json.load(fp)                     # load default settings dictionary
fp.close()

def setup_from_saved():
    ''' Write default settings to the pyboard. '''
    apic.writeI2C(default['gainpos'],0)
    time.sleep(0.1)
    apic.writeI2C(default['threshpos'],1)
    time.sleep(0.1)
    apic.setpolarity(setpolarity=default['polarity'])
    apic.drain_socket()

def checkerror():
    errorbox.config(text=apic.errorstatus)

apic = F.APIC(default['timeout'],default['ipv4']) # connect to the APIC

setup_from_saved()

root = Tk()
root.title('WAQ System')
#root.wm_iconbitmap('dAPIC.bmp')

I2Cframe = LabelFrame(root,text='I2C Digital Potentiometer Control')
I2Cframe.grid(row=1,column=1,columnspan=5,rowspan=4)

ADCframe = LabelFrame(root,text='DAQ')
ADCframe.grid(row=5,column=1,columnspan=3,rowspan=2,sticky=W)

diagnostic = LabelFrame(root,text='Calibration Tools')
diagnostic.grid(row=5,column=5,rowspan=2,columnspan=2)

polarityframe = LabelFrame(root,text='Polarity Switch.')
polarityframe.grid(row=5,column=4,rowspan=2)

histframe = LabelFrame(root, text='Graph Config')
histframe.grid(row=7,column=1, columnspan=3,rowspan=5,sticky=NW)

saveframe = LabelFrame(root, text='Savemode')
saveframe.grid(row=7,column=4, rowspan=2, sticky=NW)

#==================================================================================#
# I2C TOOLS FRAME:
# Define read/write functions and map to buttons/sliders for each pot.
# Define scan function to return the two I2C addresses.
#==================================================================================#

# See apic.readI2C and apic.I2C for explanation of functions.
def read():
    try:
        apic.readI2C()
        Ireadlabel.config(text='Gain: %i , Threshold: %i' % (apic.posGAIN,apic.posTHRESH))
    except:
        errorbox.config(text='TIMEOUT')

def scan():
    try:
        apic.scanI2C()      
        Iscanlabel.config(text=str(apic.I2Caddrs))
    except:
        errorbox.config(text='TIMEOUT')

# Define int variables for the widgets to reference
var0 = IntVar()
var1 = IntVar()

def write0():
    gain = var0.get()           # retrieve 8 bit int value from the position of the slider
    apic.writeI2C(gain,0)       # call the write function with this value

def write1():
    threshold = var1.get()
    apic.writeI2C(threshold,1)

# Widget definitions and placement
Iread = Button(I2Cframe,text='POTENTIOMETER VALS',command=read, width=18)
Iread.grid(row=1,column=1)

Ireadlabel = Label(I2Cframe,text='---')
Ireadlabel.grid(row=2,column=1)

Iscan = Button(I2Cframe,text='I2C ADDRESS LIST',command=scan,width=18)
Iscan.grid(row=3,column=1)

Iscanlabel = Label(I2Cframe,text='---',bd=10)
Iscanlabel.grid(row=4,column=1)

# GAIN POT BUTTON
W0B = Button(I2Cframe,text='SET GAIN',command=write0, width=15)
W0B.grid(row=1,column=5,sticky=W)

W0S = Scale(I2Cframe,orient=HORIZONTAL,tickinterval=32,resolution=1,
    from_=0,to=255,length=300,variable=var0)
W0S.grid(row=1,column=3,columnspan=2)

# THRESHOLD POT BUTTON
W1B = Button(I2Cframe,text='SET THRESHOLD',command=write1, width=15)
W1B.grid(row=3,column=5, sticky=W)

W1S = Scale(I2Cframe,orient=HORIZONTAL,tickinterval=32,resolution=1,
    from_=0,to=255,length=300,variable=var1)
W1S.grid(row=3,column=3,columnspan=2)

div = Label(I2Cframe, text='           ').grid(row=1,column=2,rowspan=4)

#==================================================================================#
# ADC CONTROL FRAME
# GRID: 2R 3C
#==================================================================================#
numadc=StringVar()

def ADCi():
    apic.drain_socket()
    progress['value'] = 0                               # reset progressbar
    datapoints = int(numadc.get())                      # get desired number of samples from the tkinter text entry
    apic.ADCi(datapoints,progress,root)                 # take data using ADCi protocol

    global histogram
    histogram = plt.Figure(dpi=100)
    global ax1
    ax1 = histogram.add_subplot(111)
    
    apic.hdat = numpy.average(apic.setunits(apic.data, default['units']), axis=1)        # average the ADC peak data over the columns
    apic.hdat = apic.hdat[apic.hdat>0]                  # remove zeros (controvertial feature)
    
    # set titles and axis labels
    ax1.hist(apic.hdat,apic.bins,apic.boundaries,color='b', edgecolor='black')
    ax1.set_title(default['title'])
    ax1.set_xlabel(default['xlabel']+ (" (%s)") % (apic.units))
    ax1.set_ylabel(default['ylabel'])
    
    #plt.savefig('histdata\histogram'+str(apic.raw_dat_count)+'.png')
    
    # add the plot to the gui
    global bar1
    bar1 = FigureCanvasTkAgg(histogram, root)   
    bar1.get_tk_widget().grid(row=1,column=7,columnspan=1,rowspan=10)
    apic.drain_socket()                     # drain socket to clear interrupt overflows

    if apic.savemode:
        apic.savedata(apic.data)            # save raw data
    else:
        pass


# Add ADC frame widgets
ADCi_label = Label(ADCframe, text='Interrupt Samples:')
ADCi_label.grid(row=1,column=1)

ADCi_entry = Entry(ADCframe,textvariable=numadc)
ADCi_entry.grid(row=1,column=2)

ADC_out = Button(ADCframe, command=ADCi,text='Start',width=10)#,state=DISABLED)
ADC_out.grid(row=1,column=3)

progress = ttk.Progressbar(ADCframe,value=0,maximum=apic.samples,length=350) # add a progress bar
progress.grid(row=2,column=1,columnspan=3)

#==================================================================================#
# POLARITY FRAME
# GRID: 2r 1c
#==================================================================================#

POL = IntVar()

def pselect():
    apic.setpolarity(setpolarity=POL.get())

# Add polarity widgets
ppolarity = Radiobutton(polarityframe,command=pselect,text='Positive',value=1,variable=POL)
ppolarity.grid(row=1,column=1,sticky=W)

npolarity = Radiobutton(polarityframe,command=pselect,text='Negative',value=0,variable=POL)
npolarity.grid(row=2,column=1,sticky=W)

#==================================================================================#
# HISTOGRAM FRAME
#==================================================================================#

titlestr = StringVar()
xstr = StringVar()
ystr = StringVar()
cbins = StringVar()
unitvar = StringVar()
lowbound = StringVar()
highbound = StringVar()

def set_t():
    ax1.cla()
    ax1.set_title(titlestr.get())
    ax1.set_xlabel(xstr.get())
    apic.title = titlestr.get()
    apic.xlabel = xstr.get()+unitvar.get()
    apic.ylabel = ystr.get()
    apic.bins = int(cbins.get())
    ax1.set_ylabel(ystr.get())
    apic.boundaries = (int(lowbound.get()),int(highbound.get()))
    
    apic.hdat = apic.setunits(apic.hdat,unitvar.get())
    ax1.hist(apic.hdat, int(cbins.get()), (int(lowbound.get()),int(highbound.get())), color='b', edgecolor='black')
    
    bar1 = FigureCanvasTkAgg(histogram, root)   
    bar1.get_tk_widget().grid(row=1,column=7,columnspan=1,rowspan=10)

ewidth = 30
t_entr = Entry(histframe, textvariable = titlestr, width =ewidth)
t_entr.grid(row=1,column=2,columnspan=2)
x_entr = Entry(histframe, textvariable = xstr, width = ewidth)
x_entr.grid(row=2,column=2,columnspan=2)
y_entr = Entry(histframe, textvariable = ystr,width = ewidth)
y_entr.grid(row=3,column=2,columnspan=2)
bins_entr = Entry(histframe,textvariable = cbins,width = ewidth)
bins_entr.grid(row=4,column=2, columnspan=2)
lowbound_entr = Entry(histframe, textvariable=lowbound, width = int(ewidth/2))
lowbound_entr.grid(row=5,column=2)
highbound_entr = Entry(histframe, textvariable=highbound, width = int(ewidth/2))
highbound_entr.grid(row=5,column=3)

t_entr.insert([0],default['title'])
x_entr.insert([0],default['xlabel']+ (" (%s)") % (apic.units))
y_entr.insert([0], default['ylabel'])
bins_entr.insert([0], default['bins'])
lowbound_entr.insert([0],default['boundaries'][0])
highbound_entr.insert([0], default['boundaries'][1])

mvbutton = Radiobutton(histframe,text='mV',value='mV',variable=unitvar)
mvbutton.grid(row=1,column=4,sticky=W)
adubutton = Radiobutton(histframe,text='ADU',value='ADU',variable=unitvar)
adubutton.grid(row=2,column=4,sticky=W)

setbutton = Button(histframe, text='SET', command=set_t, width = 5)
setbutton.grid(row=3,column=4)

t_label = Label(histframe, text = 'TITLE:')
t_label.grid(row=1,column=1,sticky=W)
x_label = Label(histframe, text = 'X AXIS:')
x_label.grid(row=2,column=1,sticky=W)
y_label = Label(histframe, text = 'Y AXIS:')
y_label.grid(row=3,column=1,sticky=W)
bins_label = Label(histframe, text= 'BINS:')
bins_label.grid(row=4,column=1,sticky=W)
bound_label = Label(histframe, text='BOUNDS')
bound_label.grid(row=5,column=1,sticky=W)

#==================================================================================#
# CALIBRATION FRAME
#==================================================================================#

errorbox = Message(root,text='Error messages.',
    bg='white',relief=RIDGE,width=220)
errorbox.grid(row=7,column=5,sticky=NW)

def f(x,a,b,c):
    ''' Second order tranfer function to fit to pulse strecher input/output curve.\n
    f(x,a,b,c)\n
    Arguments:\n
    \t x: x axis data
    \t a: x**2 fit param
    \t b: gradient fit param
    \t c: offset fit param'''
    return a*x**2 + b*x + c

def calibrate():
    apic.calibration()
    cf1, cf2  = curve_fit(f, apic.inputpulses, apic.outputpulses)
    a,b,c = cf1
    fig = plt.figure()
    global ax2
    ax2 = fig.add_subplot(122)
    ax2.plot(apic.inputpulses,apic.outputpulses,label='raw data')
    ax2.plot(apic.inputpulses,f(apic.inputpulses,a,b,c),
        label='y=%fx^2 + %fx + %fc' % (a,b,c),linestyle='--')
    ax2.legend()
    fig.savefig('calibration.png')
    # Set apic objects for the gain/offset of the fit
    apic.calibgradient = b
    apic.caliboffset = c
    caliblabel.config(text='y=%sx^2+%sx+%s' % (str(a),str(b),str(c)))
    apic.drain_socket()
#    ADCout.config(state=NORMAL)

def rateaq():
    ''' Acquire the rate of the source. '''
    rate = apic.rateaq()
    ratelabel.config(text=str(rate)+'Hz')
    apic.drain_socket()

calibration = Button(diagnostic,text='CALIBRATE GAIN',
    command=calibrate, width = 14)
calibration.grid(row=1,column=1,sticky=W)

ratebutton = Button(diagnostic,text='MEASURE RATE'
    ,command = rateaq, width = 14)
ratebutton.grid(row=2,column=1,sticky=W)

ratelabel = Label(diagnostic,text='---')
ratelabel.grid(row=2,column=2)

caliblabel = Label(diagnostic,text='---')
caliblabel.grid(row=1,column=2)
#==================================================================================#
# SAVEMODE FRAME
#==================================================================================#
savemode_var = BooleanVar()

def setsavemode():
    apic.savemode = savemode_var.get()

save_on = Checkbutton(saveframe, text=("%r")%(apic.savemode),
     command = setsavemode, onvalue=True, offvalue=False, variable=savemode_var)
save_on.grid(row=1,column=1)

#==================================================================================#
# TOP MENU FUNCTIONS + OPTIONS
#==================================================================================#

menubar = Menu(root)

def connect():
    apic.sock.connect(default['ipv4'])

def disconnect():
    apic.sock.close()

def quit():
    apic.sock.close()
    root.quit()

def savesettings():
    ''' Save updated config settings so that setup is preserved on restart. '''
    
    fp = open("APICconfig.json","w")

    default['calibgradient'] = apic.calibgradient
    default['timeout'] = apic.tout
    default['gainpos'] = apic.posGAIN
    default['threshpos'] = apic.posTHRESH
    default['savemode'] = apic.savemode
    default['polarity'] = apic.polarity
    default['units'] = apic.units
    default['title'] = apic.title
    default['ylabel'] = apic.ylabel
    default['bins'] = apic.bins
    default['boundaries'] = apic.boundaries
    
    json.dump(default,fp,indent=1)
    fp.close()

def adcwd():
    apic.sendcmd(2,0)
    #progress['value'] = 0                   # reset progressbar
    #datapoints = int(numadc.get())          # get desired number of samples from the tkinter text entry
    apic.adcwd_test(100,progress,root)     # take data using ADCi protocol


# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label='Save', command=savesettings)
filemenu.add_command(label="Connect", command=connect)
filemenu.add_command(label="Disconnect", command=disconnect)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=quit)
menubar.add_cascade(label="Menu", menu=filemenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About", command=adcwd)
menubar.add_cascade(label="Help", menu=helpmenu)

root.config(menu=menubar)       # display menubar
root.mainloop()                 # run main gui program