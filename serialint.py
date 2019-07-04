import serial
import time

ser = serial.Serial('COM5', 115200,timeout=1)

file = open('rawdata.txt','w')
#for x in range(100):
time.sleep(10)

raw_data = ser.read_until(bytes('end','utf-8'))

file.write(str(raw_data))

file.close()


