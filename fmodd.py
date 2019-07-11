# Make a dAPIC class to add to the main code, possible to update aspects such as I2C addresses, call method to read/write/scan

def I(address,method):
'''I2C control of the APIC, I(address,method). Address can be 1,0 and represents the width or gain digital pot (actual address hard coded into python board). Method is read 'r', write 'w', scan's' - check micropython docs for reading and writing to I2C devices. '''

    if address != 0 or 1:
        raise ValueError('Function only takes addresses 0, 1 for gain, width pots.')
    
    if method == 'r':
        sercom = bytearray([0,address])
        ser.write(sercom)
        reply = ser.read(1)
        print(int.from_bytes(reply,'little'))

    elif method == 'w':
        sercom = bytearray([1,address])
        value = int(input('value\n>'))
        ser.write(sercom)
        ser.write(bytes([value]))

    elif method == 's':
        sercom = bytearray([0,2])
        ser.write(sercom)
        time.sleep(0.5)
        if ser.in_waiting()>0:
            print(ser.readline()[:-2])
        else:
            print('No I2C devices found.')

    return None




def A():
'''ADC control for pyboard. A()  '''
elif cmd == 'A':

reads = int(input('Readings:\n>'))
breads = reads.to_bytes(4,'little',signed=False)
data = numpy.zeros((reads,1000),dtype='uint16')

sercom = bytearray([2,0])
read = bytearray(2000)
ser.write(sercom)
ser.write(breads)

for x in range(reads):
    ser.readinto(read)
    data[x,:] = numpy.frombuffer(read,dtype='uint16')
else:
    print('Successful datalogging!')


plt.figure()

datalong = data.flatten()
x = numpy.arange(len(datalong))
plt.plot(x,datalong)

plt.show()

numpy.savetxt('data.txt',data)

elif cmd == 'AD':
reads = 1000
data = numpy.zeros((reads,1000),dtype='uint16')
sercom = bytearray([2,1])
read = bytearray(2000)
ser.write(sercom)
d0 = datetime.datetime.now()


for x in range(reads):
    ser.readinto(read)
    data[:] = numpy.frombuffer(read,dtype='uint16')

d1 = datetime.datetime.now()
d = d1-d0
d = d.total_seconds()
print(d)

elif cmd == 'Ic':
pass
elif cmd == 'R':
ser = serial.Serial('COM7', 115200,timeout=0.5)
else:
print('Invalid command.')

ser.reset_input_buffer()
ser.reset_output_buffer()