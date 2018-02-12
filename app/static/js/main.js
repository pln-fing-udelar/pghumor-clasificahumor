var $tweet;
var $rating;
var $caption;
var $homeContent;
var $aboutUsContent;
var $aboutUsLink;

var tweets = [];
var index = 0;

var page = 0;

$(document).ready(function () {
    setupElements();

    getRandomTweets();

    $rating.rating({
        captionElement: '#caption',
        clearCaption: '¡Votá!',
        showClear: false,
        starCaptions: {1: "¡Malísimo!", 2: "Malo", 3: "Ni ni", 4: "Bueno", 5: "¡Buenísimo!"},
        size: 'lg',

        step: 1
    });

    $rating.on('rating.change', function (event, value) {
        vote(value);
        setTimeout(function () {
            $caption.text("¡Gracias!");
            setTimeout(function () {
                $rating.rating('clear');
            }, 800);
        }, 700);
    });
});

function setupElements() {
    $tweet = $('#tweet');
    $rating = $('#rating');
    $caption = $('#caption');
    $homeContent = $('#home-content');
    $aboutUsContent = $('#about-us-content');
    $aboutUsLink = $('#about-us-link');
}

function showTweet() {
    $tweet.html(tweets[index].text_tweet.replace(/\n/mg, '<br/>')).text();
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

    $.post('vote', {tweet_id: tweets[oldIndex].id_tweet, vote: voteOption}, function (tweet) {
        tweets[oldIndex] = tweet;
    }, 'json');

    showTweet();
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
