from tkinter import *
import tkinter.ttk as ttk
import numpy

### SETUP
root = Tk()
#root.geometry('1000x500')
root.title('APIC')
#root.wm_iconbitmap('dAPIC.bmp')

### I2C CONTROL
I2Cframe = LabelFrame(root,text='I2C Digital Potentiometer Control')
I2Cframe.grid(row=1,column=1,columnspan=6,rowspan=4)

def read():
    Ireadlabel.config(text='Gain: %i , Width: %i' % (128,128))

def scan():
    Iscanlabel.config(text=str([44,45]))

Iread = Button(I2Cframe,text='Potentiometer Values',command=read).grid(row=1,column=1)
Ireadlabel = Label(I2Cframe,text='---')
Ireadlabel.grid(row=2,column=1)

Iscan = Button(I2Cframe,text='I2C Addresses',command=scan).grid(row=3,column=1)
Iscanlabel = Label(I2Cframe,text='---',bd=10)
Iscanlabel.grid(row=4,column=1)

#Dividing up IR and IW
divide = Label(I2Cframe,text='                ').grid(row=1,column=2,rowspan=6,columnspan=2)

# I2C WRITING WITH SLIDERS
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

### ADC Control
numadc=StringVar()
def stringcontrol():
    vals = numadc.get() 
    ADCout.config(text=vals)

ADCframe = LabelFrame(root,text='Measurement Tools')
ADCframe.grid(row=5,column=1,columnspan=5,rowspan=5,sticky=W)

ADCil = Label(ADCframe, text='Interrupt Samples:')
ADCil.grid(row=1,column=1)

ADCie = Entry(ADCframe,textvariable=numadc)
ADCie.grid(row=1,column=2)

ADCout = Button(ADCframe, command=stringcontrol)
ADCout.grid(row=1,column=3)

def pselect():
    return None

divide = Label(ADCframe,text='Polarity:').grid(row=1,column=5)

ppolarity = Radiobutton(ADCframe,command=pselect,text='Positive',value=1)
ppolarity.grid(row=2,column=5,sticky=W)
npolarity = Radiobutton(ADCframe,command=pselect,text='Negative',value=2)
npolarity.grid(row=3,column=5,sticky=W)

divide = Label(ADCframe,text='                   ').grid(row=1,
    column=4,rowspan=6)

diagnostic = LabelFrame(root,text='Diagnostic Frame:')
diagnostic.grid(row=5,column=6,columnspan=6)
errorbox = Message(diagnostic,text='Error 404 nothing to display here except an error that is long!',
    bg='white',relief=RIDGE,width=220)
errorbox.grid(row=1,column=1)

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

# display the menu
root.config(menu=menubar)
root.mainloop()