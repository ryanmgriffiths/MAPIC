from tkinter import *
import tkinter.ttk as ttk
import numpy
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import time
from array import array
import MAPIC_functions as MAPIC
import json
from scipy.stats import norm
import scipy.optimize as sciop
#==================================================================================#
# SETUP
# Reload previous setup from json file,
# create new apic object, connect + setup class variables for socket connection.
# init root window
# setup each frame with a label and allocate sizes with grid.
#==================================================================================#

fp = open("MAPIC_utils/MAPIC_config.json","r")          # load config file in read mode
default = json.load(fp)                                 # load default settings dictionary
fp.close()

def load_settings():
    ''' Write default settings to the pyboard. '''
    apic.writeI2C(default['gainpos'],0)
    time.sleep(0.1)
    apic.writeI2C(default['threshpos'],1)
    time.sleep(0.1)
    apic.setpolarity(setpolarity=default['polarity'])
    lowbound_entr.insert([0],default['boundaries'][0])
    highbound_entr.insert([0], default['boundaries'][1])

    apic.drain_socket()

def checkerror():
    errorbox.config(text=apic.errorstatus)

apic = MAPIC.APIC(default['timeout'],default['ipv4']) # connect to the APIC

#load_settings()

root = Tk()
root.title('WIRELESS MAPIC')
root.wm_iconbitmap('MAPIC_utils/MAPIC.ico')

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

normfitframe = LabelFrame(root, text='Gaussian Fit')
normfitframe.grid(row=7,column=4,columnspan=1,rowspan=1)


#==================================================================================#
# NORMAL FIT FRAME
#==================================================================================#
nlowbound = StringVar()
nhighbound = StringVar()

def normfit():
    binx = []
    biny = []
    for x, y in zip(apic.binedges[:-1],apic.binvals):
        if x >= int(nlowbound.get()) and x <= int(nhighbound.get()):
            binx.append(x)
            biny.append(y)
        else:
            pass
    
    binx = numpy.array(binx)
    biny = numpy.array(biny)
    apic.mean, apic.std = norm.fit(binx)

    def gaussian(x,A):
        return A*numpy.exp(-0.5*((x-apic.mean)/apic.std)**2)
            
    global ax
    popt, pcov = sciop.curve_fit(gaussian, binx, biny)
    print(popt)
    biny = gaussian(binx,popt[0])
    ax.plot( binx, biny, color='r') #legend =r'$, \bar x = $' + str(apic.mean) + r'$, \sigma = $' + str(apic.std) + ', Resolution = ' + str((2*FWHMval)/apic.mean) )

boundaries_label = Label(normfitframe, text = 'FIT BOUNDARIES')
boundaries_label.grid(row=1,column=1,columnspan=3)

normal_high_bound = Entry(normfitframe,textvariable=nhighbound, width=8)
normal_high_bound.grid(row=2,column=3)

to_divider = Label(normfitframe, text='to')
to_divider.grid(row=2,column=2)

normal_low_bound = Entry(normfitframe,textvariable=nlowbound, width=8)
normal_low_bound.grid(row=2,column=1)

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
# ADCi: is legacy python ADC Datalogging routine.
# ADC_DMA: is designed to be used with the DMA stream and so contains the bit shifting
# needed to extract data. Also the plotting is more advanced.
#==================================================================================#
numadc=StringVar()

def ADCi():
    apic.drain_socket()
    progress['value'] = 0                               # reset progressbar
    datapoints = int(numadc.get())                      # get desired number of samples from the tkinter text entry
    apic.ADCi(datapoints,progress,root)                 # take data using ADCi protocol

    global histogram
    histogram = plt.Figure(dpi=100)
    global ax
    ax = histogram.add_subplot(111)

    apic.savedata(apic.data,'adc')            # save raw data
    apic.raw_dat_count += 1
    
    apic.data = numpy.average(apic.setunits(apic.data, default['units']), axis=1)        # average the ADC peak data over the columns
    apic.data = apic.data[apic.data>0]                  # remove zeros (controvertial feature)
    
    # set titles and axis labels
    apic.binvals, apic.binedges, patchs = ax.hist(apic.data,apic.bins,apic.boundaries,color='b', edgecolor='black')
    ax.set_title(default['title'])
    ax.set_xlabel(default['xlabel']+ (" (%s)") % (apic.units))
    ax.set_ylabel(default['ylabel'])
        
    # add the plot to the gui
    global bar1
    bar1 = FigureCanvasTkAgg(histogram, root)   
    bar1.get_tk_widget().grid(row=1,column=7,columnspan=1,rowspan=10)
    apic.drain_socket()                     # drain socket to clear interrupt overflows


def ADC_DMA():
    progress['value'] = 0                               # reset progressbar
    datapoints = int(numadc.get())                      # get desired number of samples from the tkinter text entry
    apic.adc_peak_find(datapoints,progress,root)
    
    global histogram
    histogram = plt.Figure(dpi=100)
    global ax
    ax = histogram.add_subplot(111)
    ax.minorticks_on()
    ax.tick_params(axis='y', which ='major',direction='in', width=1, length=16,right=True,left=True )
    ax.tick_params(axis='y', which='minor',direction='in',width =1, length=8,right=True,left=True )
    
    ax.tick_params(axis='x', which ='major',direction='in', width=1, length=5,bottom=True,top=True )
    ax.tick_params(axis='x', which='minor',direction='in',width =1, length=3,bottom=True,top=True)

    apic.data = apic.setunits(apic.data, default['units'])
    # apic.data_time -> time with us resolution in same order as above

    apic.binvals, apic.binedges, patchs = ax.hist(apic.data,apic.bins,apic.boundaries,color='b', edgecolor='black')
    ax.set_title(default['title'])
    ax.set_xlabel(default['xlabel']+ (" (%s)") % (apic.units))
    ax.set_ylabel(default['ylabel'])

    if nlowbound.get == "" or nhighbound.get() == "":
        pass
    else:
        normfit()

    # add the plot to the gui
    global bar1
    bar1 = FigureCanvasTkAgg(histogram, root)   
    bar1.get_tk_widget().grid(row=1,column=7,columnspan=1,rowspan=10)

    apic.savedata(apic.data,'adc')            # save data
    apic.savedata(apic.data_time,'time')       # save time data
    apic.raw_dat_count += 1


# Add ADC frame widgets
ADCi_label = Label(ADCframe, text='Interrupt Samples:')
ADCi_label.grid(row=1,column=1)

ADCi_entry = Entry(ADCframe,textvariable=numadc)
ADCi_entry.grid(row=1,column=2)

ADC_out = Button(ADCframe, command=ADC_DMA,text='Start',width=10)#,state=DISABLED)
ADC_out.grid(row=1,column=3)

progress = ttk.Progressbar(ADCframe,value=0,maximum=apic.samples,length=350) # add a progress bar
progress.grid(row=2,column=1,columnspan=3)

#==================================================================================#
# POLARITY FRAME
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

# CLEAR HISTOGRAM + SET NEW OPTIONS
def set_t():
    ax.cla()
    ax.set_title(titlestr.get())
    ax.set_xlabel(xstr.get())
    apic.title = titlestr.get()
    apic.xlabel = xstr.get()+(" (%s)" % (unitvar.get()))
    apic.ylabel = ystr.get()
    apic.bins = int(cbins.get())
    ax.set_ylabel(ystr.get())
    apic.boundaries = (int(lowbound.get()),int(highbound.get()))
    ax.minorticks_on()
    ax.tick_params(axis='y', which ='major',direction='in', width=1, length=16,right=True,left=True )
    ax.tick_params(axis='y', which='minor',direction='in',width =1, length=8,right=True,left=True )

    ax.tick_params(axis='x', which ='major',direction='in', width=1, length=6,bottom=True,top=True )
    ax.tick_params(axis='x', which='minor',direction='in',width =1, length=3,bottom=True,top=True)
    apic.data = apic.setunits(apic.data,unitvar.get())
    apic.binvals, apic.binedges, patchs = ax.hist(apic.data, int(cbins.get()), (int(lowbound.get()),int(highbound.get())), color='b', edgecolor='black')
    if nlowbound.get == "" or nhighbound.get() == "":
        pass
    else:
        normfit()    
    bar1 = FigureCanvasTkAgg(histogram, root)   
    bar1.get_tk_widget().grid(row=1,column=7,columnspan=1,rowspan=10)

# SAVE HISTOGRAM WITH CURRENT SETTINGS
def savefig():
    figtemp = plt.figure()
    ax1 = figtemp.add_subplot(111)
    ax1.set_title(titlestr.get())
    apic.title = titlestr.get()
    apic.xlabel = xstr.get()+(" (%s)" % (unitvar.get()))
    ax1.set_xlabel(apic.xlabel)
    apic.ylabel = ystr.get()
    apic.bins = int(cbins.get())
    ax1.set_ylabel(ystr.get())
    apic.boundaries = (int(lowbound.get()),int(highbound.get()))
    ax1.minorticks_on()
    ax1.tick_params(axis='y', which ='major',direction='in', width=1, length=16,right=True,left=True )
    ax1.tick_params(axis='y', which='minor',direction='in',width =1, length=8,right=True,left=True )
    
    ax1.tick_params(axis='x', which ='major',direction='in', width=1, length=5,bottom=True,top=True )
    ax1.tick_params(axis='x', which='minor',direction='in',width =1, length=3,bottom=True,top=True)

    apic.data = apic.setunits(apic.data,unitvar.get())
    apic.binvals, apic.binedges, patchs = ax1.hist(apic.data, int(cbins.get()), (int(lowbound.get()),int(highbound.get())), color='b', edgecolor='black')
    
    figtemp.savefig('histdata\histogram'+apic.createfileno(apic.raw_dat_count-1)+'.png')

ewidth = 35
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
savebutton = Button(histframe, text='SAVE', command=savefig, width = 5)
savebutton.grid(row=4,column=4)

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
errorbox.grid(row=12,column=2,sticky=NW)

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
# TOP MENU FUNCTIONS + OPTIONS
#==================================================================================#

menubar = Menu(root)

def quit():
    apic.sock.close()
    root.quit()

def savesettings():
    ''' Save updated config settings so that setup is preserved on restart. '''
    
    fp = open("MAPIC_utils/MAPIC_config.json","w")

    default['calibgradient'] = apic.calibgradient
    default['timeout'] = apic.tout
    default['gainpos'] = apic.posGAIN
    default['threshpos'] = apic.posTHRESH
    default['polarity'] = apic.polarity
    default['title'] = apic.title
    default['bins'] = apic.bins
    default['boundaries'] = apic.boundaries
    
    json.dump(default,fp,indent=1)
    fp.close()

# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label='Load',command=setup_from_saved)
filemenu.add_command(label='Save', command=savesettings)
filemenu.add_separator()
filemenu.add_command(label="Exit", command=quit)
menubar.add_cascade(label="Menu", menu=filemenu)

root.config(menu=menubar)       # display menubar
root.mainloop()                 # run main gui program