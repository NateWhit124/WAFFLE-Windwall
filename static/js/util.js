/**
 * Converts a speed in meters per second to miles per hour
 * @param  {number} speedMs - speed in meters per second
 * @return {number} Speed in miles per hour
 */
export function msToMph(speedMs) {
    return speedMs * 2.237;
}

/**
 * Converts a speed in meters per second to feet per second
 * @param  {number} speedMs - speed in meters per second
 * @return {number} Speed in feet per second
 */
export function msToFps(speedMs) {
    return speedMs * 3.281;
}

export function clamp(x, min, max) {
    return Math.max(min, Math.min(x,max))
}

export function hsvToRgb(h, s, v) {
    let f = (n, k = (n + h / 60) % 6) =>
        v - v * s * Math.max(Math.min(k, 4 - k, 1), 0);
    let r = Math.round(f(5) * 255);
    let g = Math.round(f(3) * 255);
    let b = Math.round(f(1) * 255);
    return [r, g, b];
}

export function getFanColor(pct) {
    let h = 192;
    let s = 0.82;
    let v = 0.25 + (pct / 100)*(0.75);
    return hsvToRgb(h,s,v);
}

export function getFanLabelColor(pct) {
    // Get the background RGB
    let [r, g, b] = getFanColor(pct);

    // Calculate luminance (perceived brightness)
    // Formula: https://www.w3.org/TR/AERT/#color-contrast
    let luminance = (0.299 * r + 0.587 * g + 0.114 * b);

    // If luminance is high, use black text; otherwise, use white text
    if (luminance > 140) {
        return [0, 0, 0]; // black
    } else {
        return [255, 255, 255]; // white
    }
}