let $continue;
let $prolific_id_txt;

let answers = {};

let prolific_id = "";
let prolific_session_id = "";
let study_id = "";

$(document).ready(function () {
    setupElements();
    setUiListeners();
});

function getUrlVars()
{
    var vars = [], hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for(var i = 0; i < hashes.length; i++)
    {
        hash = hashes[i].split('=');
        vars.push(hash[0]);
        vars[hash[0]] = hash[1];
    }
    return vars;
}

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
    urlVars = getUrlVars();
    if ("PROLIFIC_PID" in urlVars) {
        prolific_id = urlVars["PROLIFIC_PID"];
    }
    if ("SESSION_ID" in urlVars) {
        prolific_session_id = urlVars["SESSION_ID"];
    }
    if ("STUDY_ID" in urlVars) {
        study_id = urlVars["STUDY_ID"];
    }
    $prolific_id_txt = $("#prolific-id-txt");
    $prolific_id_txt.val(prolific_id);
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

    prolific_id_val = $("#prolific-id-txt").val().trim();
    if (prolific_id_val == "") {
        $.mdtoast("Please specify your Prolific ID", {duration: 3000});
        return;
    }

    $.post('annotator', {
        prolific_id: prolific_id_val,
        prolific_session_id: prolific_session_id,
        study_id: study_id,
        question1: answers['question1'],
        question2: answers['question2'],
        question3: answers['question3'],
        question4: answers['question4'],
        question5: answers['question5'],
        question6: answers['question6']
    }, function (msg) {
        if (msg == "OK-SURVEY") {
            window.location.replace("votes.html");
        } else if (msg == "OK-NO-SURVEY") {
            window.location.replace("survey.html");
        } else if (msg == "NO-CONSENT") {
            window.location.replace("noconsent.html");
        } else {
            $.mdtoast(msg, {duration: 3000})
        }
    }, 'json');
}
