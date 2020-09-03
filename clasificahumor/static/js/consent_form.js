let $continue;

let answers = {};

$(document).ready(function () {
    setupElements();
    setUiListeners();
});

function setupYesNoQuestion(yes_btn,no_btn,question,answers) {
    yes_btn.click(function () {
        if (!yes_btn.hasClass('toggle-button-down')) {
            answers[question] = 'y';
            yes_btn.addClass('toggle-button-down');
            no_btn.removeClass('toggle-button-down');
        }
    });
    no_btn.click(function () {
        if (!no_btn.hasClass('toggle-button-down')) {
            answers[question] = 'n';
            no_btn.addClass('toggle-button-down');
            yes_btn.removeClass('toggle-button-down');
        }
    });
}

function setupElements() {
    $continue = $('#continue-btn');
    setupYesNoQuestion($('#question1-y'),$('#question1-n'),'question1',answers);
    setupYesNoQuestion($('#question2-y'),$('#question2-n'),'question2',answers);
    setupYesNoQuestion($('#question3-y'),$('#question3-n'),'question3',answers);
    setupYesNoQuestion($('#question4-y'),$('#question4-n'),'question4',answers);
    setupYesNoQuestion($('#question5-y'),$('#question5-n'),'question5',answers);
    setupYesNoQuestion($('#question6-y'),$('#question6-n'),'question6',answers);
}

function setUiListeners() {
    $continue.click(function () {
        continue_click();
    });
}

function continue_click() {
    if (!('question1' in answers) || !('question2' in answers) || !('question3' in answers)
        || !('question4' in answers) || !('question5' in answers) || !('question6' in answers)) {
        $.mdtoast("Please answer all questions", {duration: 3000});
        return;
    }

    $.post('annotator', {
        prolific_id: "12345abc",
        question1: answers['question1'],
        question2: answers['question2'],
        question3: answers['question3'],
        question4: answers['question4'],
        question5: answers['question5'],
        question6: answers['question6']
    }, function (msg) {
        if (msg == "OK") {
            window.location.replace("index.html");
        } else {
            $.mdtoast(msg, {duration: 3000})
        }
    }, 'json');
}
