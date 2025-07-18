import serial
from bitstring import BitArray
from typing import Optional
from enum import IntEnum
from pydantic import BaseModel, Field
import random, sys
from logging import Logger
from processing.test_serial import FakeArduino

# Byte 0 :  1 bit  turn velocity output on/off (0/1)
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
    # PWM Low
    pwm_low = packet.pwm & 0XFF
    bits.append(BitArray(uint=pwm_low, length=8))
    # PWM High
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
        device.timeout = 1
        self.device = device

    def send_packet(self, packet : Packet):
        if self.device == None:
            raise ValueError("Arduino Device has not been set.")
        bits = serialize_packet(packet)
        if self.logger is not None:
            self.logger.debug(f"Sending packet to serial device: velocity_output_on: {packet.velocity_output_on} fan_id: {packet.module_id} pwm_value: {packet.pwm}")
            self.logger.debug(f"Sending raw bytes to serial device: {bits.bin}")
        self.device.write(bits.tobytes())
        ack = self.device.read(1)[0];
        if not ack == 1:
            raise RuntimeError(f"Failed to set PWM for Module with ID {packet.module_id}; did not receive ACK response.")
        else:
            if self.logger is not None:
                self.logger.debug(f"Recieved ACK from serial device.\n")

    def send_pwm_array_command(self, pwms: list):
        for module_idx,pwm in enumerate(pwms):
            self.send_single_pwm_command(module_idx,pwm)

    def send_single_pwm_command(self, module_idx: int, pwm: int):
        bits = BitArray()
        bits.append('0b0')
        bits.append(BitArray(uint=module_idx,length=4))
        bits.append('0b000')
        pwm_low = pwm & 0xFF
        bits.append(BitArray(uint=pwm_low,length=8))
        pwm_high = pwm >> 8
        bits.append(BitArray(uint=pwm_high,length=4))
        bits.append('0b0000')
        parity = bits.count(1) & 1
        bits.append(BitArray(parity^1, length=1))
        bits.append('0b0000000')
        # print(bits)
        self.device.write(bits.tobytes())

    def decode_pwm_command(self, packet : bytes):
        value = int.from_bytes(packet, byteorder='big')
        command_type = value >> 31
        fan_id = value >> 27 & 0xF
        pwm_value = (value >> 4 & 0xF00) | (value >> 16 & 0xFF)
        return f"Command type: {command_type} fan_id: {fan_id} pwm_value: {pwm_value}\n"

    def print_loop_buffer(self):
        command_bytes = self.device.read_all()
        commands = [command_bytes[i:i+4] for i in range(0, len(command_bytes), 4)]
        for command in commands:
            print(self.decode_pwm_command(command))

if __name__=='__main__':
    # Example usage:
    # module_idx = 3, pwm = 2048 (50% of 4095)
    arduino_interface = ArduinoInterface()
    arduino_interface.device = serial.serial_for_url('loop://')
    
    arduino_interface.send_single_pwm_command(1,2048)
    print("0x"+arduino_interface.device.read(4).hex())

    # Example usage:
    # sending an array of pwm commands
    pwms = []
    for i in range(0,4095,341):
        print(i)
        pwms.append(i)
    arduino_interface.send_pwm_array_command(pwms)
    for i in range(12):
        packet = arduino_interface.device.read(4)
        print(str(i+1) + ') ' + ' '.join(f'{b:08b}' for b in packet))
        arduino_interface.decode_pwm_command(packet)
