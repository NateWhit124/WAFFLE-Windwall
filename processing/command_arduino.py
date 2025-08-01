import serial
from bitstring import BitArray
from typing import Optional
from enum import IntEnum
from pydantic import BaseModel, Field
import random, sys
from logging import Logger
from processing.test_serial import FakeArduino
import time

# Byte 0 :  1 bit  turn velocity output on/off (1/0)
# **NOTE**  A packet with Byte 0 set to 1 (turn on velocity output)
#           will IGNORE the rest of the packet (only the first bit is read)
#           4 bits Module ID
#           3 bits reserved (future / flags)

# Byte 1 :  PWM low 8 bits
# Byte 2 :  PWM high 4 bits, 4 bits reserved
# Byte 3 :  CRC-8 of bytes 0-2

class Packet(BaseModel):
    module_id : int = Field(ge=0, le=11)
    pwm : int = Field(ge=0, le=4095)
    velocity_output_on : bool = False

def serialize_packet(packet : Packet) -> BitArray:
    bits = BitArray()
    # Velocity output on/off (0/1)
    bits.append(BitArray(uint=packet.velocity_output_on, length=1))
    # Module ID
    bits.append(BitArray(uint=packet.module_id, length=4))
    # 3 bits reserved
    bits.append('0b000')
    # PWM Low (lower byte of packet.pwm)
    pwm_low = packet.pwm & 0XFF
    bits.append(BitArray(uint=pwm_low, length=8))
    # PWM High (uppder nibble of packet.pwm)
    pwm_high = packet.pwm >> 8
    bits.append(BitArray(uint=pwm_high, length=4))
    # 4 bits reserved
    bits.append('0b0000')
    # TODO: implement CRC-8
    bits.append('0b00000000')
    return bits

class ArduinoInterface:
    def __init__(self, logger : Optional[Logger] = None):
        self.device : Optional[serial.Serial | FakeArduino] = None
        self.logger : Optional[Logger] = logger

    def set_device(self, device : serial.Serial):
        device.timeout = 0.5
        self.device = device
        self.timeout = 0.5

    def send_packet(self, packet : Packet):
        if self.device == None:
            raise ValueError("Arduino Device has not been set.")
        bits = serialize_packet(packet)
        if self.logger is not None:
            self.logger.debug(f"Sending packet to serial device: velocity_output_on: {packet.velocity_output_on} fan_id: {packet.module_id} pwm_value: {packet.pwm}")
            self.logger.debug(f"Sending raw bytes to serial device: {bits.bin}")

        start_time = time.time()
        self.device.write(bits.tobytes())
        while(self.device.in_waiting == 0):
            if time.time() - start_time > self.timeout:
                raise TimeoutError("Timed out waiting for Arduino response.")

        success = self.device.readline()
        if self.logger is not None:
            if not success: self.logger.error(f"ERROR: Arduino failed to execute command.")
            elif not packet.velocity_output_on: self.logger.info(f"Arduino executed command: Set Module {packet.module_id} to PWM {packet.pwm}.")
            elif packet.velocity_output_on: self.logger.info(f"Arduino executed command: Turn velocity output {'ON' if packet.velocity_output_on else 'OFF'}.")

    def decode_pwm_command(self, packet : bytes):
        value = int.from_bytes(packet, byteorder='big')
        command_type = value >> 31
        fan_id = value >> 27 & 0xF
        pwm_value = (value >> 4 & 0xF00) | (value >> 16 & 0xFF)
        return f"Command type: {command_type} fan_id: {fan_id} pwm_value: {pwm_value}\n"
