import serial
import time

ser = serial.Serial('COM5', 115200)
raw_data = ser.read_until('end')
print(raw_data)