let $star;
let $homeContent;
let $tweet;
let $legendVote;
let $next;
let emoji;

let votes = {};

let count_votes = 0;

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
});

function setupQuestion(yes_btn,no_btn,vote_pnl,vote_btns,question,votes) {
    vote_pnl.addClass('votes-panel-hidden');
    yes_btn.click(function () {
        if (!yes_btn.hasClass('toggle-button-down')) {
            delete votes[question];
            yes_btn.addClass('toggle-button-down');
            no_btn.removeClass('toggle-button-down');
            vote_pnl.removeClass('votes-panel-hidden');
        }
    });
    no_btn.click(function () {
        if (!no_btn.hasClass('toggle-button-down')) {
            vote_pnl.children('.vote').removeClass('selected');
            votes[question] = 'n';
            no_btn.addClass('toggle-button-down');
            yes_btn.removeClass('toggle-button-down');
            vote_pnl.addClass('votes-panel-hidden');
        }
    });
    $.each(vote_btns,function (i,btn) {
        btn.click(function () {
            pieces = btn[0].id.split('-');
            option = pieces[pieces.length-1];
            votes[question] = option;
            vote_pnl.children('.vote').removeClass('selected');
            btn.addClass('selected');
        })
    });
}

function resetQuestion(yes_btn,no_btn,vote_pnl,question,votes) {
    delete votes[question];
    no_btn.removeClass('toggle-button-down');
    yes_btn.removeClass('toggle-button-down');
    vote_pnl.addClass('votes-panel-hidden');
    vote_pnl.children('.vote').removeClass('selected');
}

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
    $next = $('#next');
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

function initToggle(button) {
    button.click(function () {
        if (!button.hasClass('toggle-button-down')) {
            button.addClass('toggle-button-down');
        } else {
            button.removeClass('toggle-button-down');
        }
    });
}

function releaseToggle(button) {
    button.removeClass('toggle-button-down');
}

function setToggle(button) {
    button.addClass('toggle-button-down');
}

function setUiListeners() {
    setupQuestion($('#humor'),$('#not-humor'),$('#humor-panel'),[$('#vote-h-d'),$('#vote-h-1'),$('#vote-h-2'),$('#vote-h-3'),$('#vote-h-4'),$('#vote-h-5')],'humor',votes);
    setupQuestion($('#offensive'),$('#not-offensive'),$('#offensive-panel'),[$('#vote-o-1'),$('#vote-o-2'),$('#vote-o-3'),$('#vote-o-4'),$('#vote-o-5')],'offensive',votes);
    setupQuestion($('#personal'),$('#not-personal'),$('#personal-panel'),[$('#vote-p-1'),$('#vote-p-2'),$('#vote-p-3'),$('#vote-p-4'),$('#vote-p-5')],'personal',votes);

    $next.click(function () {
        vote();
    });

    $('#help').click();
}

function vote() {
    if (!('humor' in votes) || !('offensive' in votes) || !('personal' in votes)) {
        $.mdtoast("Please answer all questions", {duration: 3000});
        return;
    }

    const oldIndex = index;
    index = (index + 1) % tweets.length;

    tweet_ids = []
    for (i = 0; i < tweets.length; i++) {
        tweet_ids.push(tweets[i].id);
    }

    $.post('vote', {
        tweet_id: tweets[oldIndex].id,
        vote_humor: votes['humor'],
        vote_offensive: votes['offensive'],
        vote_personal: votes['personal'],
        ignore_tweet_ids: tweet_ids
    }, function (tweet) {
        tweets[oldIndex] = tweet;
        count_votes++;
        if (count_votes == 25) {
            window.location.replace("thankyou.html");
        }
    }, 'json');

    resetQuestion($('#humor'),$('#not-humor'),$('#humor-panel'),'humor',votes);
    resetQuestion($('#offensive'),$('#not-offensive'),$('#offensive-panel'),'offensive',votes);
    resetQuestion($('#personal'),$('#not-personal'),$('#personal-panel'),'personal',votes);
    showTweet();

    $.mdtoast("Vote registered. Thanks!", {duration: 3000});

    $('html,body').scrollTop(0);
}

function removeNonWords(text) {
    return text.replace(/[^\w\sáéíóúÁÉÍÓÚüÜñÑ]/g, "");
}
