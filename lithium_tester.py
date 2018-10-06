import serial
import pylithium
import time
import pickle
import signal
import random

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

signal.signal(signal.SIGINT, signal_handler)
interrupted = False

s = serial.Serial('ttyUSB0')
li = pylithium.Lithium(s)

transmitting = True
sent = []
if transmitting:
    filename = input("Enter savefile name: ")
    input("Press any key to start transmitting...")
    for packet_size in [48, 96, 128, 255]:
        for i in range(1, 101):
            packet = bytes([i].append([random.randint(0, 2**8-1) for i in range(packet_size-1)]))
            sent.append(packet)
            li.transmit(packet)
            time.sleep(0.5)
    with open(filename+".pkl","wb") as f:
        pickle.dump(sent, f) 
else:
    received = []
    while True:
        if s.in_waiting > 0:
            received.append(s.read_all())

        if interrupted:
            print("Gotta go")
            break
        
