let $star;
let $homeContent;
let $tweet;
let $humor;
let $votesAndToolbox;
let $toolbox;
let $voteClass;
let $vote1;
let $vote2;
let $vote3;
let $vote4;
let $vote5;
let $legendVote;
let $notHumor;
let $skip;
let $isOffensive;
let emoji;

let legendsShownForFirstTime = false;

const voteCodeToText = {
    1: "Nada gracioso",
    2: "Poco gracioso",
    3: "Regular",
    4: "Bueno",
    5: "¡Buenísimo!"
};

let tweets = [];
let index = 0;

$(document).ready(function () {
    setupSentry();
    setupElements();
    setupPlaceload();
    setupEmojiConverter();
    getRandomTweets();
    setUiListeners();
    moveToolboxIfOutside();
});

function setupSentry() {
    // The following key is public.
    Raven.config('https://3afb3f9917f44b2a87e6fbb070a8977b@sentry.io/298102', {
        ignoreUrls: ['localhost', '127.0.0.1']
    }).install();
}

function setupElements() {
    $star = $('*');
    $homeContent = $('#home-content');
    $tweet = $('#tweet-text');
    $humor = $('#humor');
    $votesAndToolbox = $('#votes,#toolbox');
    $toolbox = $('#toolbox');
    $voteClass = $('.vote');
    $vote1 = $('#vote-1');
    $vote2 = $('#vote-2');
    $vote3 = $('#vote-3');
    $vote4 = $('#vote-4');
    $vote5 = $('#vote-5');
    $legendVote = $('.legend-vote');
    $notHumor = $('#not-humor');
    $skip = $('#skip');
    $isOffensive = $('#is-offensive');
}

function showTweet() {
    if (tweets.length === 0) {
        console.error("No hay tweets para mostrar.");
    } else {
        $tweet.fadeOut(200, function () {
            $tweet.html(emoji.replace_unified(tweets[index].text.replace(/\n/mg, '<br/>'))).text();
            $tweet.fadeIn(200);
        });
    }
}

function setupPlaceload() {
    Placeload
        .$('#tweet-text')
        .config({speed: '1s'})
        .line(function (element) {
            return element.width(100).height(15);
        })
        .config({spaceBetween: '7px'})
        .line(function (element) {
            return element.width(100).height(15);
        })
        .config({spaceBetween: '7px'})
        .line(function (element) {
            return element.width(40).height(15);
        }).fold(function (err) {
    }, function (allElements) {
    });
}

function setupEmojiConverter() {
    // noinspection JSUnresolvedFunction
    emoji = new EmojiConvertor();
    emoji.img_set = 'twitter';
    emoji.img_sets.twitter.path = 'https://raw.githubusercontent.com/iamcal/emoji-data/a97b2d2efa64535d6300660eb2cd15ecb584e79e/img-twitter-64/';
}

function getRandomTweets() {
    $.getJSON('tweets', function (data) {
        tweets = data;
        showTweet();
    });
}

function setUiListeners() {
    $humor.click(function () {
        if (!legendsShownForFirstTime) {
            $legendVote.stop().fadeTo('slow', 1, function () {
                setTimeout(function () {
                    $legendVote.stop().fadeTo('slow', 0, function () {
                        $legendVote.css('opacity', '');
                    });
                }, 1000);
            });
            legendsShownForFirstTime = true;
        }
    });

    $humor.hover(function () {
        $votesAndToolbox.css('display', '');
    });

    $notHumor.click(function () {
        vote('x');
        $notHumor.addClass('no-hover');
    });

    $notHumor.on('mousemove mouswdown', function () {
        $notHumor.removeClass('no-hover');
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

    $('button').mouseup(function () {
        $(this).blur();
    });
}

function vote(voteOption) {
    const oldIndex = index;
    index = (index + 1) % tweets.length;

    const otherIndex = (index + 1) % tweets.length;

    $.post('vote', {
        tweet_id: tweets[oldIndex].id,
        vote: voteOption,
        ignore_tweet_ids: [tweets[index].id, tweets[otherIndex].id],
        is_offensive: $isOffensive.prop('checked'),
    }, function (tweet) {
        tweets[oldIndex] = tweet;
    }, 'json');

    showTweet();

    $.mdtoast(toastText(voteOption), {duration: 3000});

    $votesAndToolbox.fadeOut();

    $isOffensive.prop('checked', false);
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

function moveToolboxIfOutside() {
    const x = $toolbox[0].getBoundingClientRect().x;
    if (x < 0) {
        const translation = -x + 10;
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
