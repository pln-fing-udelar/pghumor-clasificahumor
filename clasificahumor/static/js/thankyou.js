let $prolific;
let $commentsTxt;

$(document).ready(function () {
    setupElements();
    setUiListeners();
});

function setupElements() {
    $prolific = $('#prolific-btn');
    $commentsTxt = $('#comments-txt');
}

function setUiListeners() {
    $prolific.click(function () {
        prolific_click();
    });
}

function prolific_click() {
    $.post('get-prolific-url', {
        comments: $commentsTxt.val()
    }, function (msg) {
        window.location.replace(msg["url"]);
    }, 'json');
}
