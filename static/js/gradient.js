const directionBtns = document.querySelectorAll('.gradient-direction');
directionBtns.forEach(directionBtn => {
    directionBtn.addEventListener('click', () => {
        directionBtns.forEach(btn => btn.classList.remove('selected'));
        directionBtn.classList.add('selected');
    });
})
