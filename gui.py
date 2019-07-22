from tkinter import *
import tkinter.ttk as ttk
import numpy

root = Tk()
#root.geometry('500x500')
root.title('APIC')
#root.wm_iconbitmap('dAPIC.bmp')

def read():
    I2Cl = Label(root,text='Gain = %i , Width = %i' % (128,128)).grid(row=2,column=1)

# I2C READING
I2Cr = Button(root,text='Read Potentiometers!',command=read).grid(row=1,column=1)
I2Cl = Label(root,text='---').grid(row=2,column=1)

#Dividing up IR and IW
divide = Label(root,text='                ').grid(row=1,column=2,rowspan=4,columnspan=2)

# I2C WRITING WITH SLIDERS
var1 = IntVar()
var0 = IntVar()

def ret0():
    output = Label(root,text=str(var0.get())).grid(row=1,column=5)
def ret1():
    output = Label(root,text=str(var1.get())).grid(row=2,column=5)

W1 = Label(root,text='Gain').grid(row=1,column=4)
W1 = Scale(orient=HORIZONTAL,tickinterval=32,resolution=1,from_=1,to=256,length=300,variable=var1).grid(row=1,column=5)

W0 = Label(root,text='Width').grid(row=2,column=4)
W0 = Scale(orient=HORIZONTAL,tickinterval=32,resolution=1,from_=1,to=256,length=300,variable=var0).grid(row=2,column=5)


menubar = Menu(root)

# create a pulldown menu, and add it to the menu bar
filemenu = Menu(menubar, tearoff=0)
filemenu.add_command(label="Open")
filemenu.add_command(label="Save")
filemenu.add_separator()
filemenu.add_command(label="Exit", command=root.quit)
menubar.add_cascade(label="File", menu=filemenu)

helpmenu = Menu(menubar, tearoff=0)
helpmenu.add_command(label="About")
menubar.add_cascade(label="Help", menu=helpmenu)




# display the menu
root.config(menu=menubar)
root.mainloop()