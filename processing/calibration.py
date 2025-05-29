from numpy import polyfit, polyval, poly1d, roots, isreal
import csv

class CalibrationFit:
    def __init__(self):
        self.calibration_data = []
        self.fit_coefs = [8,0]
        self.min_vel_ms = 0
        self.max_vel_ms = 8
    
    def init_calibration_data(self,data_filename) -> tuple[list,list,float,float]:
        self.calibration_data = []
        with open(data_filename, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # Convert each value to float and store as a tuple
                self.calibration_data.append((float(row[0]), float(row[1])))
        duty_cycles = [coord[0] for coord in self.calibration_data]
        speeds = [coord[1] for coord in self.calibration_data]
        self.fit_coefs = polyfit(speeds, duty_cycles, 3)
        self.max_vel_ms = max(speeds)
        self.min_vel_ms = min(speeds)
    
    def invert_polyfit(self,y_target):
        p = poly1d(self.fit_coefs)
        r = roots(p - y_target)
        xs = [x.real for x in r if isreal(x) and x >= self.min_vel_ms and x <= self.max_vel_ms]
        return xs[0]
    
    def get_duty_cycle_from_speed(self, speedms : float):
        if speedms == 0: return 0
        return polyval(self.fit_coefs, speedms)
    def get_speed_from_duty_cycle(self, duty_cycle : float):
        if duty_cycle==0: return 0
        return self.invert_polyfit(duty_cycle)