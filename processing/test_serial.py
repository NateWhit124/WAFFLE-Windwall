import io
from logging import Logger
from typing import Optional
from bitstring import BitArray

class FakeArduino:
    def __init__(self, logger : Optional[Logger] = None):
        self._read_buffer = io.BytesIO()
        self._write_buffer = io.BytesIO()
        self.logger : Optional[Logger] = logger
        self.in_waiting : int = 0

    def write(self, data):
        """Simulates writing data to the serial port."""
        self._write_buffer.seek(0, io.SEEK_END)  # move to end before writing
        self._write_buffer.write(data)
        
        # Read everything from start
        self._write_buffer.seek(0)
        available = len(self._write_buffer.getvalue()) - self._write_buffer.tell()

        while available >= 4:
            packet = self._write_buffer.read(4)
            available = len(self._write_buffer.getvalue()) - self._write_buffer.tell()

            if self.logger:
                bits = BitArray(packet)
                # self.logger.debug(f"FakeArduino received command: {self.decode_pwm_command(bits.tobytes())}")
                # self.logger.debug(f"FakeArduino received raw bytes: {bits.bin}")

            self.inject_input(bytes([1,0x0a]))
            self.in_waiting = 2

        # rebuild the buffer with remaining bytes
        remaining = self._write_buffer.read()
        self._write_buffer = io.BytesIO(remaining)

    def read(self, size=1):
        """Simulates reading data from the serial port."""
        return self._read_buffer.read(size)

    def readline(self):
        """Simulates reading a line."""
        return self._read_buffer.readline()

    def inject_input(self, data: bytes):
        """Put fake data into the read buffer (as if Arduino sent it)."""
        current = self._read_buffer.getvalue()[self._read_buffer.tell():]
        self._read_buffer = io.BytesIO(current + data)

    def decode_pwm_command(self, packet : bytes):
        value = int.from_bytes(packet, byteorder='big')
        velocity_output_on = value >> 31
        fan_id = value >> 27 & 0xF
        pwm_value = (value >> 4 & 0xF00) | (value >> 16 & 0xFF)
        return f"velocity_output_on: {velocity_output_on} fan_id: {fan_id} pwm_value: {pwm_value}"


    def close(self):
        pass
