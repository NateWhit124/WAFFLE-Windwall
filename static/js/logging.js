const loggingInterval = setInterval(getLogDelta, 500);
const consoleWindow = document.getElementById('console')

function getLogDelta() {
    fetch('/log', {method: 'GET'})
    .then(response => response.json())
    .then(data => {
        if(data) {
            consoleWindow.innerHTML += data;
        }
    });
}
