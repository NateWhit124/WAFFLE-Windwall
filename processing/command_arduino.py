import serial
from bitstring import BitArray
import random, sys

# Byte 0 :  1 bit  packet-type      (0 = control, 1 = toggle velocity output)
#           4 bits fan ID
#           3 bits reserved (future / flags)

# Byte 1 :  PWM low 8 bits
# Byte 2 :  PWM high 4 bits, 4 bits reserved
# Byte 3 :  CRC-8 of bytes 0-2

class ArduinoInterface:
    def __init__(self):
        self.device : serial.Serial = None

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