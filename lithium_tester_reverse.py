import argparse
import array
import serial
import struct
import time
import pylithium

BAUD_RATE = 115200

SEND_LOGFILE = "sent.log"
RECV_LOGFILE = "recv.log"

SEND_PACKET_SIZES = [255, 64, 1]
SEND_PACKET_ITERATIONS = 25
SEND_PACKET_DELAY = 1.0

RECV_PACKET_DELAY = 0.005


def log_append(log, s):
    log.write(s)
    print(s)


def send(port):
    device = serial.Serial(port, baudrate=BAUD_RATE, timeout=1.0)
    # lithium = pylithium.Lithium(device)
    log = open(SEND_LOGFILE, "a")
    log_append(log, f'[send] Starting transmit at {time.strftime("%Y-%m-%d %H:%M:%S")} ...')
    # Send packets
    for packet_size in SEND_PACKET_SIZES:
        for i in range(SEND_PACKET_ITERATIONS):
            # Create \xF0\x0D[len][iter][padding]...
            packet = b''
            # packet += b'\xF0\x0D'
            packet += struct.pack('<B', packet_size)
            packet += struct.pack('<B', i)
            packet += array.array('B', list(range(packet_size - 4))).tostring()
            try:
                # lithium.transmit(packet)
                device.write(b'\xC0\x00'+packet+b'\xC0')
            except IOError:
                log_append(log, '[send] Failed transmit!')
                continue
            log_append(log, f'[send] Transmitting: len={packet_size}, i={i}')
            time.sleep(SEND_PACKET_DELAY)


def recv(port):
    device = serial.Serial(port, baudrate=BAUD_RATE, timeout=1.0)
    log = open(RECV_LOGFILE, "a")
    buf = b''
    log_append(log, f'[send] Starting receive at {time.strftime("%Y-%m-%d %H:%M:%S")} ...')
    counter = 0
    prev_packet_id = 0
    while True:
        time.sleep(RECV_PACKET_DELAY)
        if device.in_waiting > 0:
            buf += device.read_all()
            continue
        if len(buf) > 0:
            if buf[0] != 0xF0:
                buf = buf[1:]
                continue
            if len(buf) < 2 or buf[1] != 0x0D:
                buf = buf[1:]
                continue
            # Parse packet
            if len(buf) < 4:
                log_append(log, '[recv] Recieved runt (corrupt) packet!')
                buf = b''
                continue
            packet_len = buf[2]
            packet_id = buf[3]
            if packet_id < prev_packet_id:
                print("Packets received count: %d"%(counter))
                counter = 0
            prev_packet_id = packet_id
            counter += 1
            log_append(log, f'[recv] Recieved: len={packet_len}, i={packet_id}')
            buf = b''


parser = argparse.ArgumentParser()
parser.add_argument('port', type=str)
parser.add_argument('--send', dest='send', action='store_const',
                    const=True, default=False)

args = parser.parse_args()
if args.send:
    send(args.port)
else:
    recv(args.port)
