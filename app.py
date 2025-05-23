from flask import Flask, request, render_template, jsonify
from numpy import polyfit, polyval, poly1d, roots, isreal
import csv

app = Flask(__name__)
logger = app.logger
fit_coefs = None
inv_coefs = None
calibration_data = None
max_vel_ms = -1
min_vel_ms = -1
duty_cycle_epsilon = 0.1

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
    speedms = invert_polyfit(fit_coefs, duty_cycle)
    if(speedms < min_vel_ms or speedms > max_vel_ms):
        return error_message(f'Invalid speed calculated from duty cycle: duty_cycle={duty_cycle}, speed(m/s)={speedms} which is out of bounds of min and max speeds: min={min_vel_ms}, max={max_vel_ms}')
    return jsonify({'speed_ms': speedms}), 200

@app.route('/speed-to-duty-cycle', methods=['POST'])
def speed_to_duty_cycle():
    data = request.get_json()
    if not data or 'speedms' not in data:
        return error_message('Missing required parameter: speedms')
    speedms = float(data['speedms'])
    speedms = clamp(speedms, min_vel_ms, max_vel_ms)
    duty_cycle = polyval(fit_coefs, speedms)
    if -duty_cycle_epsilon < duty_cycle < 0:
        duty_cycle = 0
    elif 1 < duty_cycle < 1 + duty_cycle_epsilon:
        duty_cycle = 1
    
    if(duty_cycle < 0 or duty_cycle > 1):
        return error_message(f'Invalid duty cycle calculated from speed: duty_cycle={duty_cycle}, speed(m/s)={speedms} which is out of bounds of min and max speeds: min={min_vel_ms}, max={max_vel_ms}')
    return jsonify({'duty_cycle': duty_cycle}), 200

def clamp(x, _min, _max):
    return max(_min, min(x,_max))

def error_message(message : str):
    return jsonify({
        'status': 'error',
        'message': message
    }), 400

def init_calibration_data(data_filename):
    data = []
    with open(data_filename, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # Convert each value to float and store as a tuple
            data.append((float(row[0]), float(row[1])))
    duty_cycles = [coord[0] for coord in data]
    speeds = [coord[1] for coord in data]
    coefs = polyfit(speeds, duty_cycles, 3)
    max_vel = max(speeds)
    min_vel = min(speeds)
    return data, max_vel, min_vel, coefs

def invert_polyfit(coeffs, y_target):
    p = poly1d(coeffs)
    r = roots(p - y_target)
    xs = [x.real for x in r if isreal(x) and x >= min_vel_ms and x <= max_vel_ms]
    return xs[0]

calibration_data, max_vel_ms, min_vel_ms, fit_coefs = init_calibration_data('test_data.csv')
app.run(host='0.0.0.0', port='5000', debug=True)