document.addEventListener('DOMContentLoaded', function() {
    const firstMoveButton = document.getElementById('first-move-button');
    const secondMoveButton = document.getElementById('second-move-button');

    firstMoveButton.addEventListener('click', playFirstMove);
    secondMoveButton.addEventListener('click', playSecondMove);
});

function playFirstMove() {
    fetch('/move_order/1', {
        method: "GET",
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(res => {
        if (res.redirected) {
            window.location.href = res.url;
        }
    })
}

function playSecondMove() {
    fetch('/move_order/2', {
        method: "GET",
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(res => {
        if (res.redirected) {
            window.location.href = res.url;
        }
    })
}
