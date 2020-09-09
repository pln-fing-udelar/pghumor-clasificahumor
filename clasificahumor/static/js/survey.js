let $continue;
let $question1;
let $question2;
let $question3;
let $question4;
let $question5;
let $question6;
let $question7;
let $question8;
let $question9;
let $question10;

$(document).ready(function () {
    setupElements();
    setUiListeners();
});

function setupElements() {
    $continue = $('#continue-btn');
    $question1 = $('#question1');
    $question2 = $('#question2');
    $question3 = $('#question3');
    $question4 = $('#question4');
    $question5 = $('#question5');
    $question6 = $('#question6');
    $question7 = $('#question7');
    $question8 = $('#question8');
    $question9 = $('#question9');
    $question10 = $('#question10');
}

function setUiListeners() {
    $continue.click(function () {
        continue_click();
    });
}

function continue_click() {
    if ($question1.val() == '-' || $question2.val() == '-' || $question3.val() == '-' || $question4.val() == '-' || $question5.val() == '-' || 
        $question6.val() == '-' || $question7.val() == '-' || $question8.val() == '-' || $question9.val() == '-' || $question10.val() == '-') {
        $.mdtoast("Please answer all questions", {duration: 3000});
        return;
    }

    $.post('personality_survey', {
        question1: $question1.val(),
        question2: $question2.val(),
        question3: $question3.val(),
        question4: $question4.val(),
        question5: $question5.val(),
        question6: $question6.val(),
        question7: $question7.val(),
        question8: $question8.val(),
        question9: $question9.val(),
        question10: $question10.val()
    }, function (msg) {
        if (msg == "OK") {
            window.location.replace("votes.html");
        } else {
            $.mdtoast(msg, {duration: 3000})
        }
    }, 'json');
}
