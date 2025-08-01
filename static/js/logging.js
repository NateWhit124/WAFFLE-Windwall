const loggingInterval = setInterval(getLogDelta, 100);
const consoleWindow = document.getElementById('console')

function getLogDelta() {
    fetch('/log', {method: 'GET'})
    .then(response => response.json())
    .then(data => {
        if(data) {
            const scrollIsAtBottom = (consoleWindow.scrollTop + consoleWindow.clientHeight >= consoleWindow.scrollHeight - 1);
            consoleWindow.innerHTML += data;
            if(scrollIsAtBottom) consoleWindow.scrollTop = consoleWindow.scrollHeight;
        }
    });
}
