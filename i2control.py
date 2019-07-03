from pyb import I2C
import time
i2c = I2C(1, I2C.MASTER,baudrate=20000)

print(i2c.scan())
print(i2c.is_ready(0x2C))

b = bytearray([0x00,255])

i2c.send(b,addr=0x2C)
time.sleep(0.5)

print(int.from_bytes(i2c.recv(1,addr=0x2C),'big'))