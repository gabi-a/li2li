class Lithium():

    SYNC_CHARS = b'\x48\x65'
    DIRECTION_INTO_LITHIUM = b'\x10'
    DIRECTION_FROM_LITHIUM = b'\x20'

    def __init__(self, port):
        self.port = port

    def _do_command(self, command_code, payload=None, expect_response=False, ignore_reply=False):

        command = bytearray()

        if payload is not None:
            size = len(payload)
        else:
            size = 0

        command.extend(self.SYNC_CHARS)
        command.extend(self.DIRECTION_INTO_LITHIUM)
        command.extend(command_code)
        command.append(size >> 8)
        command.append(size & 0xFF)
        header_check = self._checksum(command[2:])
        command.extend(header_check)
        if payload is not None:
            command.extend(payload)
        payload_check = self._checksum(command[2:])
        command.extend(payload_check)

        self.port.write(command)

        if ignore_reply:
            return

        self.port.read_until(terminator=self.SYNC_CHARS)
        rx_direction = self.port.read()
        if rx_direction != self.DIRECTION_FROM_LITHIUM:
            raise IOError("Lithium Direction Ack Failed")
        rx_command = self.port.read()
        if rx_command != command_code:
            raise IOError(f"Lithium Command Ack Failed\nCommand code expected: {command_code}\nCommand code received: {rx_command}")

        if expect_response:
            rx_size = self.port.read(2)
            rx_header_check = self.port.read(2)
            if rx_header_check != self._checksum(rx_direction + rx_command + rx_size):
                raise IOError("Lithium Header Checksum Ack Failed")
            rx_payload = self.port.read(int.from_bytes(rx_size, 'big'))
            rx_payload_check = self.port.read(2)
            if rx_payload_check != self._checksum(rx_direction + rx_command + rx_size
                                                + rx_header_check + rx_payload):
                raise IOError("Lithium Payload Checksum Ack Failed")

            return rx_payload
        else:
            ack = self.port.read(2)
            if ack == b'\x0A\x0A':
                return True
            else:
                raise IOError("Lithium Payload Ack Failed")

    def _checksum(self, data):
        ckA = 0
        ckB = 0
        for i in data:
            ckA = ckA + i
            ckB = ckB + ckA

        ckA %= 256
        ckB %= 256

        return bytes([ckA, ckB])

    def transmit(self, message):
        print("Lithium transmitting",message)
        self._do_command(b'\x03', message)

    def noop(self):
        self._do_command(b'\x01')

    def read_telemetry(self, ignore_reply=False):
        return self._do_command(b'\x07', expect_response=True, ignore_reply=ignore_reply)

    def set_pa(self, setting):
        self._do_command(b'\x20', setting)

    def flush_input(self):
        self.port.flushInput()

    def read_buffer(self):
        return self.port.read_all()

    def read_config(self):
        return self._do_command(b'\x05', expect_response=True, ignore_reply=False)

    def write_flash(self, hash):
        self._do_command(b'\x08', hash)

if __name__ == '__main__':
    import serial
    import time
    import hashlib

    li = Lithium(serial.Serial('COM7'))
    
    config = li.read_config()
    time.sleep(1)
    hash = hashlib.md5(config).digest()
    print(len(hash))
    print(hash)
    li.write_flash(hash)
    