from flask import Flask, request, render_template, jsonify
import processing.calibration
import processing.command_arduino
import serial

app = Flask(__name__)
logger = app.logger

duty_cycle_epsilon = 0.1
calibration_fit = processing.calibration.CalibrationFit()
calibration_fit.init_calibration_data('test_data.csv')
arduino_interface = processing.command_arduino.ArduinoInterface()
arduino_interface.device = serial.serial_for_url('loop://')

@app.route('/', methods=['GET'])
def landing():
    return render_template('main.html')

@app.route('/duty-cycle-to-speed', methods=['POST'])
def duty_cycle_to_speed():
    data = request.get_json()
    if not data or 'duty_cycle' not in data:
        return error_message('Missing required parameter: duty_cycle')
    if data['duty_cycle'] == None:
        return error_message(f'Duty cycle cannot be None')
    duty_cycle = float(data['duty_cycle'])
    duty_cycle = clamp(duty_cycle, 0, 1)
    speedms = calibration_fit.get_speed_from_duty_cycle(duty_cycle)
    if(speedms < calibration_fit.min_vel_ms or speedms > calibration_fit.max_vel_ms):
        return error_message(f'Invalid speed calculated from duty cycle: duty_cycle={duty_cycle}, speed(m/s)={speedms} which is out of bounds of min and max speeds: min={calibration_fit.min_vel_ms}, max={calibration_fit.max_vel_ms}')
    return jsonify({'speed_ms': speedms}), 200

@app.route('/speed-to-duty-cycle', methods=['POST'])
def speed_to_duty_cycle():
    data = request.get_json()
    if not data or 'speedms' not in data:
        return error_message('Missing required parameter: speedms')
    speedms = float(data['speedms'])
    speedms = clamp(speedms, calibration_fit.min_vel_ms, calibration_fit.max_vel_ms)
    duty_cycle = calibration_fit.get_duty_cycle_from_speed(speedms)
    if -duty_cycle_epsilon < duty_cycle < 0:
        duty_cycle = 0
    elif 1 < duty_cycle < 1 + duty_cycle_epsilon:
        duty_cycle = 1
    
    if(duty_cycle < 0 or duty_cycle > 1):
        return error_message(f'Invalid duty cycle calculated from speed: duty_cycle={duty_cycle}, speed(m/s)={speedms} which is out of bounds of min and max speeds: min={calibration_fit.min_vel_ms}, max={calibration_fit.max_vel_ms}')
    return jsonify({'duty_cycle': duty_cycle}), 200

@app.route('/apply-velocities', methods=['POST'])
def apply_velocities():
    data = request.get_json()
    pwms = data['pwms']
    arduino_interface.send_pwm_array_command(pwms)
    arduino_interface.print_loop_buffer()
    return "good", 200

def clamp(x, _min, _max):
    return max(_min, min(x,_max))

def error_message(message : str):
    return jsonify({
        'status': 'error',
        'message': message
    }), 400


app.run(host='0.0.0.0', port='5000', debug=True)