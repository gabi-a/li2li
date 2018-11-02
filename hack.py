import serial
import time

magic = b'\xc0\x00\x80\x80\x80\x80\x80\x80\x02\x82\x82\x82\x82\x82\x82\x04\xAB\xCD'

message = b'Hello'*20

packet = magic + message + b'\xc0'

s = serial.Serial('/dev/ttyUSB0',115200)

while True:
    s.write(packet)
    time.sleep(2)