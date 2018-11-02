import serial

s = serial.Serial('COM7')

packet = b''

packet += b'H'
packet += b'e'
packet += b'\x10'
packet += b'\x08'
packet += b'\x00'
packet += b'\x10'
packet += b'('
packet += b'h'
packet += b'\x9b'
packet += b' '
packet += b'O'
packet += b'\xc6'
packet += b'_'
packet += b'\x0f'
packet += b'\x1e'
packet += b'`'
packet += b'\x7f'
packet += b'\xc1'
packet += b'\x82'
packet += b'\x89'
packet += b'm'
packet += b'\x81'
packet += b'\xc1'
packet += b'\x12'
packet += b'\x80'
packet += b'H'

s.write(packet)