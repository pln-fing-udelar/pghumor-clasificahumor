let $prolific;

$(document).ready(function () {
    setupElements();
    setUiListeners();
});

function setupElements() {
    $prolific = $('#prolific-btn');
}

function setUiListeners() {
    $prolific.click(function () {
        prolific_click();
    });
}

function prolific_click() {
    $.post('get-prolific-url', {
    }, function (msg) {
        window.location.replace(msg["url"]);
    }, 'json');
}
