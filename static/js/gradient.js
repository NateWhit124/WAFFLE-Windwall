import { applyGradientInput, unitTypes } from "./fan-grid.js";     
import { gridWidth, gridHeight } from "./main.js";

const directionBtns = document.querySelectorAll('.gradient-direction');
directionBtns.forEach(directionBtn => {
    directionBtn.addEventListener('click', () => {
        directionBtns.forEach(btn => btn.classList.remove('selected'));
        directionBtn.classList.add('selected');
    });
})

export function applyGradient() {
    let start = +document.getElementById("gradient-start-input").value;
    let end = +document.getElementById("gradient-end-input").value;
    start = Math.min(Math.max(start, 0), 100);
    end = Math.min(Math.max(end, 0), 100);
    let dir = [0,0];
    document.querySelectorAll(".gradient-direction").forEach(direction => {
        if(direction.classList.contains("selected")) {
            dir = [+direction.dataset.dirX, +direction.dataset.dirY];
        }
    });
    const mag = Math.sqrt(dir[0]**2 + dir[1]**2);
    const dirNorm = [dir[0]/mag,dir[1]/mag];
    const units = unitTypes.PCT;
    let gradient = Array(gridWidth);
    let maxValue = 0;
    for(let i=0; i<gridWidth; i++) {
        gradient[i] = Array(gridWidth);
        for(let j=0; j<gridHeight; j++) {
            let positionNormX = i;
            let positionNormY = j;
            if(dir[0] < 0) {
                positionNormX = (gridWidth - 1 - i);
            }
            if(dir[1] < 0) {
                positionNormY = (gridHeight - 1 - j);
            }
            gradient[i][j] = Math.sqrt((positionNormX*dirNorm[0])**2 + (positionNormY*dirNorm[1])**2);
            maxValue = gradient[i][j] > maxValue ? gradient[i][j] : maxValue;
        }
    }
    for(let i=0; i<gridWidth; i++) {
        for(let j=0; j<gridHeight; j++) {
            gradient[i][j] = (gradient[i][j] / maxValue) * (end-start) + start;
        }
    }
    applyGradientInput(gradient,units);
}

const applyGradientBtn = document.getElementById("apply-gradient-button");
applyGradientBtn.addEventListener('click', () => applyGradient());
