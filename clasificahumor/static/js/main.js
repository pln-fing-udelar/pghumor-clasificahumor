var $homeContent;
var $tweet;
var $humor;
var $showToolbox;
var $toolbox;
var $vote1;
var $vote2;
var $vote3;
var $vote4;
var $vote5;
var $notHumor;
var $skip;
var $aboutUsContent;
var $aboutUsLink;

var voteCodeToText = {
    1: "Nada gracioso",
    2: "Poco gracioso",
    3: "Regular",
    4: "Bueno",
    5: "¡Buenísimo!"
};

var tweets = [];
var index = 0;

var page = 0;

$(document).ready(function () {
    setupElements();

    getRandomTweets();

    if (canHover()) {
        $humor.addClass('btn-not-clickable');
    } else {
        $humor.click(function () {
            $showToolbox.prop('checked', !$showToolbox.prop('checked'));
        });
    }

    $notHumor.click(function () {
        vote('x');
    });

    $vote1.click(function () {
        vote('1');
    });

    $vote2.click(function () {
        vote('2');
    });

    $vote3.click(function () {
        vote('3');
    });

    $vote4.click(function () {
        vote('4');
    });

    $vote5.click(function () {
        vote('5');
    });

    $skip.click(function () {
        vote('n');
    });

    $("button").mouseup(function () {
        $(this).blur();
    });

    moveToolboxIfOutside();
});

function setupElements() {
    $tweet = $('#tweet-text');
    $humor = $('#humor');
    $showToolbox = $('#show-toolbox');
    $toolbox = $('#toolbox');
    $vote1 = $('#vote-1');
    $vote2 = $('#vote-2');
    $vote3 = $('#vote-3');
    $vote4 = $('#vote-4');
    $vote5 = $('#vote-5');
    $notHumor = $('#not-humor');
    $skip = $('#skip');
    $homeContent = $('#home-content');
    $aboutUsContent = $('#about-us-content');
    $aboutUsLink = $('#about-us-link');
}

function showTweet() {
    if (tweets.length === 0) {
        console.error("No hay tweets para mostrar.");
    } else {
        $tweet.html(tweets[index].text.replace(/\n/mg, '<br/>')).text();
    }
}

function getRandomTweets() {
    $.getJSON('tweets', function (data) {
        tweets = data;
        showTweet();
    });
}

function vote(voteOption) {
    var oldIndex = index;
    index = (index + 1) % tweets.length;

    $.post('vote', {tweet_id: tweets[oldIndex].id, vote: voteOption}, function (tweet) {
        tweets[oldIndex] = tweet;
    }, 'json');

    showTweet();

    $.mdtoast(toastText(voteOption), {
        duration: 3000
        /*action: function() {
            //undo();
            toast.hide();
        },
        actionText: "Deshacer",
        interaction: true*/
    });
}

function toastText(voteOption) {
    if (voteOption === 'x') {
        return "Clasificado como no humorístico. ¡Gracias!";
    } else if (voteOption === 'n') {
        return "Tweet salteado. ¡Gracias!";
    } else {
        return "Clasificado como "
            + removeNonWords(voteCodeToText[Number(voteOption)]).toLowerCase()
            + ". ¡Gracias!";
    }
}

function removeNonWords(text) {
    return text.replace(/[^\w\sáéíóúÁÉÍÓÚüÜñÑ]/g, "");
}

function showHome() {
    if (page !== 0) {
        page = 0;
        $aboutUsLink.removeClass();
        $aboutUsContent.css('display', 'none');
        $homeContent.css('display', 'block');
    }
}

function moveToolboxIfOutside() {
    var x = $toolbox[0].getBoundingClientRect().x;
    if (x < 0) {
        var translation = - x + 10;
        addPxToLeft($toolbox, translation);
        addPxToLeft($vote1, translation);
        addPxToLeft($vote2, translation);
        addPxToLeft($vote3, translation);
        addPxToLeft($vote4, translation);
        addPxToLeft($vote5, translation);
    }
}

function addPxToLeft(element, translation) {
    element.css('left', (parseInt(element.css('left')) + translation).toString() + "px");
}

function canHover() {
    return window.matchMedia('(hover: hover)').matches;
}

function showAboutUs() {
    if (page !== 1) {
        page = 1;
        $aboutUsLink.addClass('active');
        $aboutUsContent.css('display', 'initial');
        $homeContent.css('display', 'none');
    }
}
