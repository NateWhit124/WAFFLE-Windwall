#include <Adafruit_PWMServoDriver.h>
#define PACKETSIZE 4
typedef uint32_t Packet;

Adafruit_PWMServoDriver PWMDriver = Adafruit_PWMServoDriver();

struct Command {
    bool velocity_output_on;
    uint8_t module_id;
    uint16_t pwm;
};

Command decode_packet(Packet packet);
uint8_t toggle_velocity_output(bool on);
uint8_t setModulePWM(uint8_t module_id, uint16_t pwm);

void setup() {
    Serial.begin(9600); 
}

uint8_t packet_buffer[PACKETSIZE];
void loop() {
    if (Serial.available() >= PACKETSIZE) {
        for (uint8_t i=0; i<PACKETSIZE; i++) {
            packet_buffer[i] = Serial.read();
        }
        Packet packet = ((uint32_t)packet_buffer[3]) |
                  ((uint32_t)packet_buffer[2] << 8) |
                  ((uint32_t)packet_buffer[1] << 16) |
                  ((uint32_t)packet_buffer[0] << 24);
        Command command = decode_packet(packet);
        uint8_t success;
        String status_msg;

        // TOGGLE VELOCITY OUTPUT
        if (command.velocity_output_on) {
            success = toggle_velocity_output(true);
            if (success) {
                status_msg = "Executed: velocity_output_on=" + String(command.velocity_output_on) + ", module_id=" + String(command.module_id) + ", pwm=" + String(command.pwm);
            }
            else {
                status_msg = "ERROR: failed to toggle velocity output.";
            }
        }

        // VELOCITY CONTROL
        else {
            setModulePWM(command.module_id, command.pwm);
            success = 1;
            if (success) {
                status_msg = "Executed: velocity_output_on=" + String(command.velocity_output_on) + ", module_id=" + String(command.module_id) + ", pwm=" + String(command.pwm);
            }
            else {
                status_msg = "ERROR: failed to set PWM for Module ID: " + String(command.module_id);
            }
        }
        Serial.println("1");
    }
}

Command decode_packet(Packet packet) {
    Command c;
    c.velocity_output_on = packet >> 31;
    c.module_id = (packet >> 27) & 0xF;
    uint16_t pwm_low = (packet >> 16) & 0xFF;
    uint16_t pwm_high = (packet >> 12) & 0xF;
    c.pwm = (pwm_low) | (pwm_high << 8);
    return c;
}

uint8_t toggle_velocity_output(bool on) {
    if (on) {

    }
    else {

    }
}
uint8_t setModulePWM(uint8_t module_id, uint16_t pwm) {
    PWMDriver.setPWM(module_id,0,pwm);
}
