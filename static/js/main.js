import { initGrid } from './fan-grid.js'

initGrid(4, 3, 60);

const tabs = document.querySelectorAll('.tab');
tabs.forEach(tab => {
    const id = tab.id;
    const tabPage = document.getElementById(id.replace('-tab','-page'));
    tab.addEventListener('click', (e) => {
        tab.classList.add('selected');
        tabPage.classList.add('selected');
        const otherTabs = document.querySelectorAll('.tab');
        otherTabs.forEach(otherTab => {
            if(otherTab != e.currentTarget) {
                otherTab.classList.remove('selected');
            }
        })
        const otherPages = document.querySelectorAll('.tab-page')
        otherPages.forEach(otherPage => {
            if(otherPage != tabPage) {
                otherPage.classList.remove('selected');
            }
        })
    });
});

const basicInputTab = document.getElementById('basic-input-tab');
basicInputTab.classList.add('selected');
const basicInputPage = document.getElementById('basic-input-page');
basicInputPage.classList.add('selected');


const velocityInput = document.getElementById('velocity-input');
velocityInput.addEventListener('input', () => {
    let val = velocityInput.value;

    // Limit total length (excluding decimals)
    if (val.length > 3 && !val.includes('.')) {
        val = val.slice(0, 3);
    }

    // Clamp to 0–100
    let num = parseFloat(val);
    if (!isNaN(num)) {
        if (num > 100) val = "100";
        if (num < 0) val = "0";
    }

    // Limit to 2 decimal places if a dot is present
    val = val.replace(/^(\d+)(\.\d{0,2})?.*$/, (_, intPart, decPart) => {
        return intPart + (decPart || '');
    });

    // Strip one leading zero (but not from '0.' or '0')
    if (/^0[0-9]/.test(val)) {
        val = val.replace(/^0/, '');
    }

    // Only update value if it's changed (prevents cursor jump)
    if (velocityInput.value !== val) {
        velocityInput.value = val;
    }
});

