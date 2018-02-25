var $homeContent;
var $tweet;
var $notHumor;
var $rating;
var $caption;
var $skip;
var $aboutUsContent;
var $aboutUsLink;

var voteCodeToText = {
    1: "¡Horrible!",
    2: "Malo",
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

    $notHumor.click(function() {
        vote('x');
    });

    $rating.rating({
        captionElement: '#caption',
        clearCaptionClass: 'hidden-caption',
        emptyStar: '<i class="glyphicon glyphicon-star" style="color: #e3e3e3"></i>',
        showClear: false,
        size: 'lg',
        starCaptions: voteCodeToText,
        step: 1
    });

    $rating.on('rating:change', function (event, value) {
        vote(value);
    });

    $skip.click(function () {
        vote('n');
    })
});

function setupElements() {
    $tweet = $('#tweet-text');
    $notHumor = $('#not-humor');
    $rating = $('#rating');
    $caption = $('#caption');
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

    $rating.rating('reset');

    $.mdtoast(toastText(voteOption), {
        duration: 3000
        /*action: function() {
            //undo();
            toast.hide();
        },
        actionText: "Deshacer",
        interaction: true*/
    });

    //$('#funniness').css('visibility', 'hidden');
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

function showAboutUs() {
    if (page !== 1) {
        page = 1;
        $aboutUsLink.addClass('active');
        $aboutUsContent.css('display', 'initial');
        $homeContent.css('display', 'none');
    }
}
