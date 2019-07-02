import serial
import time


ser = serial.Serial('COM5', 115200, timeout=1)
ser.open()

ser.send('ready')

time.sleep(10)

data = ser.readlines()