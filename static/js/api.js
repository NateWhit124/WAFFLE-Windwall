import { clamp } from './util.js'
/**
 * Communicates with the backend Python script to convert a PWM duty cycle (0 to 1)
 * to the corresponding fan speed in m/s.
 * @param  {number} dutyCycle - The PWM duty cycle, from 0 to 1.
 * @return {number} The corresponding speed in m/s.
 */
export async function dutyCycleToSpeed(dutyCycle) {
    if(dutyCycle < 0 || dutyCycle > 1) {
        console.error("Invalid duty cycle input: " + dutyCycle);
        return -1;
    }
    if(dutyCycle == 0) return 0;

    const response = await fetch('/duty-cycle-to-speed', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'duty_cycle': dutyCycle })
    });
    if (!response.ok) {
        const errorData = await response.json();
        console.error('Backend error:', errorData.message);
        throw new Error(errorData.message);
    }
    const data = await response.json();
    return data.speed_ms;
}

/**
 * Communicates with the backend Python script to convert a desired fan speed in m/s
 * to the corresponding PWM duty cycle (0 to 1).
 * If the requested speed is greater than the maximum possible, returns 1 (100% duty cycle).
 * @param  {number} speedms - The desired speed in m/s.
 * @return {number} The corresponding duty cycle, from 0 to 1.
 */
export async function speedToDutyCycle(speedms) {
    const response = await fetch('/speed-to-duty-cycle', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 'speedms': speedms })
    });
    if (!response.ok) {
        const errorData = await response.json();
        console.error('Backend error:', errorData.message);
        throw new Error(errorData.message);
    }
    const data = await response.json();
    return data.duty_cycle;
}
