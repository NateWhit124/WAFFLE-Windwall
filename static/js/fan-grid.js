import { hsvToRgb, getFanColor, getFanLabelColor } from './util.js'
import { dutyCycleToSpeed, speedToDutyCycle, sendPWMs } from './api.js'

const gridContainer = document.querySelector('.fan-selection-grid');
document.addEventListener('contextmenu', (event) => {event.preventDefault();});
let isDragging = false;
var _boxWidth = -1;
var _gridWidth, _gridHeight;
let fanArray, originalFanState;
let mouseStartRow, mouseStartCol, mouseLastRow, mouseLastCol;

let isSelecting = true;
const selectToolButton = document.getElementById('select-tool-button');
const deselectToolButton = document.getElementById('deselect-tool-button');
selectToolButton.addEventListener('click', () => {
    isSelecting = true
    selectToolButton.classList.add('selected');
    deselectToolButton.classList.remove('selected');
});
deselectToolButton.addEventListener('click', () => {
    isSelecting = false
    selectToolButton.classList.remove('selected');
    deselectToolButton.classList.add('selected');
});

const selectAllBtn = document.getElementById('select-all-button');
selectAllBtn.addEventListener('click', () => selectAll())
const deselectAllBtn = document.getElementById('deselect-all-button');
deselectAllBtn.addEventListener('click', () => deselectAll())

const velocityInput = document.getElementById('velocity-input');
const applyVelocityBtn = document.getElementById('apply-velocity-button');
applyVelocityBtn.addEventListener('click', () => {applyVelocityInput(velocityInput.value)});

const unitTypes = Object.freeze({
    PCT: 0,
    SPEEDMS: 1
});
let units = unitTypes.PCT;
const unitsLabel = document.getElementById('units-label');
const velocityInputUnitsLabel = document.getElementById('velocity-input-units-label');
unitsLabel.innerText = "Units: Percent";
velocityInputUnitsLabel.innerText = "%";

const showPctBtn = document.getElementById('show-pct-button');
showPctBtn.classList.add('selected');
showPctBtn.addEventListener('click', () => { 
    units = unitTypes.PCT; updateLabels();
    unitsLabel.innerText = "Units: Percent";
    velocityInputUnitsLabel.innerText = "%";
    showPctBtn.classList.add('selected');
    showSpeedBtn.classList.remove('selected');
});
const showSpeedBtn = document.getElementById('show-speed-button');
showSpeedBtn.addEventListener('click', () => {
    units = unitTypes.SPEEDMS; updateLabels();
    unitsLabel.innerText = "Units: meters/sec";
    velocityInputUnitsLabel.innerText = "m/s";
    showSpeedBtn.classList.add('selected');
    showPctBtn.classList.remove('selected');
});

class Fan {
    constructor(row, col) {
        this.row = row;
        this.col = col;
        this.isSelected = false;
        this.pct = 0; // percentage from 0 to 100
        this.speed = 0; // speed in METERS PER SECOND
        this.velocityCallbacks = {
            [unitTypes.PCT]: this.setPct.bind(this),
            [unitTypes.SPEEDMS]: this.setSpeedMs.bind(this)
        }

        // creating fan-box div element
        this.element = document.createElement('div');
        this.element.classList.add('fan-box');

        // creating pct-text span element
        this.label = document.createElement('span');
        this.label.classList.add('fan-label');
        this.label.textContent = this.pct + '%';
        this.element.appendChild(this.label);
        this.setPct(this.pct)
    }
    highlight() {
        let [r, g, b] = getFanColor(Number(this.pct)+30) //small increase to the pct to increase the lightness of the box
        this.element.style.backgroundColor = `rgb(${r},${g},${b})`;
    }
    unhighlight() {
        let [r, g, b] = getFanColor(this.pct) //small increase to the pct to increase the lightness of the box
        this.element.style.backgroundColor = `rgb(${r},${g},${b})`;
    }
    select() {
        this.isSelected = true;
        this.element.classList.add('selected');
    }
    deselect() {
        this.isSelected = false;
        this.element.classList.remove('selected');
    }
    updateLabel() {
        if (units == unitTypes.PCT) {
            this.label.textContent = parseFloat(this.pct.toFixed(2)) + '%';
        }
        else if (units == unitTypes.SPEEDMS) {
            this.label.textContent = parseFloat(this.speed.toFixed(2));
        }
    }
    async setPct(pct) {
        pct = Number(pct)
        if(pct < 0 || pct > 100) {
            console.error("Invalid pct input: " + pct);
            return;
        }
        this.pct = pct;
        this.speed = await dutyCycleToSpeed(+pct/100);
        this.updateLabel();
        let [r, g, b] = getFanColor(pct);
        this.element.style.backgroundColor = `rgb(${r},${g},${b})`;
        [r, g, b] = getFanLabelColor(pct);
        this.label.style.color = `rgb(${r},${g},${b})`;
    }
    async setSpeedMs(speedMs) {
        speedMs = Number(speedMs)
        const dutyCycle = await speedToDutyCycle(speedMs);
        this.pct = dutyCycle * 100;
        this.speed = await dutyCycleToSpeed(this.pct / 100);
        if(this.pct < 0 || this.pct > 100) {
            console.error("Invalid pct from speed.\nSpeed: ",speedMs,"\nPct: ",pct);
            return;
        }
        this.updateLabel();
        let [r, g, b] = getFanColor(this.pct);
        this.element.style.backgroundColor = `rgb(${r},${g},${b})`;
        [r, g, b] = getFanLabelColor(this.pct);
        this.label.style.color = `rgb(${r},${g},${b})`;
    }
}

export function initGrid(gridWidth, gridHeight, boxWidth) {
    _boxWidth = boxWidth;
    _gridWidth = gridWidth;
    _gridHeight = gridHeight;
    document.documentElement.style.setProperty('--fanWidth', _boxWidth + 'px');
    document.documentElement.style.setProperty('--fanHeight', _boxWidth + 'px');
    fanArray = Array.from({ length: gridHeight }, () => new Array(gridWidth).fill(null));

    gridContainer.style.gridTemplateRows = `repeat(${gridHeight}, var(--fanHeight))`
    gridContainer.style.gridTemplateColumns = `repeat(${gridWidth}, var(--fanWidth))`;

    for(let row = 0; row < gridHeight; row++) {
        for(let col = 0; col < gridWidth; col++) {
            // create the fanBox div element
            const fan = new Fan(row, col);
            fanArray[row][col] = fan;
            gridContainer.appendChild(fan.element);
        }
    }
    originalFanState = fanArray.map(row => row.map(fan => fan.element.className));
}

function selectAll() {
    fanArray.forEach(row => {
        row.forEach(fan => {
            fan.select();
        })
    })
}

function deselectAll() {
    fanArray.forEach(row => {
        row.forEach(fan => {
            fan.deselect();
        })
    })
}

async function applyVelocityInput(value) {
    let pcts = [];
    for (const row of fanArray) {
        for (const fan of row) {
            if (fan.isSelected) {
                await fan.velocityCallbacks[units](value);
                pcts.push(fan.pct);
            }
        }
    }
    sendPWMs(pcts);
}

function updateLabels() {
    fanArray.forEach(row => {
        row.forEach(fan => {
            fan.updateLabel();
        })
    })
}

gridContainer.addEventListener('mousedown', (event) => {
    isDragging = true;
    const containerRect = gridContainer.getBoundingClientRect();
    const mouseX = event.clientX - containerRect.left;
    const mouseY = event.clientY - containerRect.top;
    mouseStartRow = Math.floor(mouseY / _boxWidth);
    mouseStartCol = Math.floor(mouseX / _boxWidth);

    // select or deselect box depending on the tool selected
    if(isSelecting && event.button === 0) {fanArray[mouseStartRow][mouseStartCol].select()}
    else if(!isSelecting || event.button === 2) {fanArray[mouseStartRow][mouseStartCol].deselect()}

    // copy original fanArray so that box selection can be undone during mousemove events
    originalFanState = fanArray.map(row => row.map(fan => fan.element.className));

    // save mouseLastRow and mouseLastCol to skip box selection checking if the mouse grid position doesnt change
    mouseLastRow = mouseStartRow;
    mouseLastCol = mouseStartCol;
});

gridContainer.addEventListener('mousemove', (event) => {
    const containerRect = gridContainer.getBoundingClientRect();
    const mouseX = event.clientX - containerRect.left;
    const mouseY = event.clientY - containerRect.top;
    let mouseRow = Math.floor(mouseY / _boxWidth);
    let mouseCol = Math.floor(mouseX / _boxWidth);
    mouseRow = Math.max( 0, Math.min(mouseRow, _gridHeight-1) ); // clamp between 0 and _gridHeight-1
    mouseCol = Math.max( 0, Math.min(mouseCol, _gridWidth-1) ); // clamp between 0 and _gridWidth-1


    //unhighlight the last highlighted box
    if(mouseLastRow != null && mouseLastCol != null) {
        fanArray[mouseLastRow][mouseLastCol].unhighlight();
    }
    // if not dragging, highlight the hovered box
    if (!isDragging) {
        fanArray[mouseRow][mouseCol].highlight();
        mouseLastRow = mouseRow;
        mouseLastCol = mouseCol;
        return;
    }

    // return if the mouseRow and mouseCol haven't changed
    if(mouseRow == mouseLastRow && mouseCol == mouseLastCol) return;
    // Reset all boxes to their original state
    //  allows for moving box selection around
    let minRow = Math.min(mouseStartRow, mouseLastRow);
    let maxRow = Math.max(mouseStartRow, mouseLastRow);
    let minCol = Math.min(mouseStartCol, mouseLastCol);
    let maxCol = Math.max(mouseStartCol, mouseLastCol);
    for (let row = minRow; row <= maxRow; row++) {
        for (let col = minCol; col <= maxCol; col++) {
            fanArray[row][col].element.className = originalFanState[row][col];
        }
    }
    // save last row and col for the above check next mousemove event
    mouseLastRow = mouseRow;
    mouseLastCol = mouseCol;

    // Select boxes between mouseStartRow/Col and mouseRow/Col
    minRow = Math.min(mouseStartRow, mouseRow);
    maxRow = Math.max(mouseStartRow, mouseRow);
    minCol = Math.min(mouseStartCol, mouseCol);
    maxCol = Math.max(mouseStartCol, mouseCol);

    // set the state of all fans within the selection box
    for (let row = minRow; row <= maxRow; row++) {
        for (let col = minCol; col <= maxCol; col++) {
            if(isSelecting && event.buttons & 1) {fanArray[row][col].select()}
            else if(!isSelecting || event.buttons & 2) {fanArray[row][col].deselect()}
        }
    }
});
gridContainer.addEventListener('mouseout', (event) => {
    fanArray[mouseLastRow][mouseLastCol].unhighlight();
});

document.addEventListener('mouseup', () => {
    isDragging = false;
});
