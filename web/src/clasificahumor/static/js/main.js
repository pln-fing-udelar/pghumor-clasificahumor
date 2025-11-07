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
let $voteCount;
let $consent;
let $consentForm;
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

function getParameterByName(name, url = window.location.href) {
  name = name.replace(/[\[\]]/g, "\\$&");
  const regex = new RegExp(`[?&]${name}(=([^&#]*)|&|#|$)`);
  const results = regex.exec(url);
  if (!results) {
    return null;
  }
  if (!results[2]) {
    return "";
  }
  return decodeURIComponent(results[2].replace(/\+/g, " "));
}

const PROLIFIC_TASK_TWEET_COUNT = 200;

const prolificId = getParameterByName("PROLIFIC_PID");
const isAProlificSession = Boolean(prolificId);
let voteCount = 0;

$(document).ready(main);

function main() {
  setupSentry();
  setupElements();
  setupPlaceload();
  setupEmojiConverter();
  getRandomTweets();
  setUiListeners();
  moveToolboxIfOutside();
  setupProlificSessionIfNeeded();
}

function setupSentry() {
  // The following key is public.
  Raven.config("https://3afb3f9917f44b2a87e6fbb070a8977b@sentry.io/298102", {
    ignoreUrls: ["localhost", "127.0.0.1"]
  }).install();
}

function setupElements() {
  $star = $("*");
  $homeContent = $("#home-content");
  $tweet = $("#tweet-text");
  $humor = $("#humor");
  $votesAndToolbox = $("#votes,#toolbox");
  $toolbox = $("#toolbox");
  $voteClass = $(".vote");
  $vote1 = $("#vote-1");
  $vote2 = $("#vote-2");
  $vote3 = $("#vote-3");
  $vote4 = $("#vote-4");
  $vote5 = $("#vote-5");
  $legendVote = $(".legend-vote");
  $notHumor = $("#not-humor");
  $skip = $("#skip");
  $isOffensive = $("#is-offensive");
  $voteCount = $("#vote-count");
  $consent = $("#consent");
  $consentForm = $("#consent form");
}

function showTweet() {
  if (tweets.length === 0) {
    console.error("No hay tweets para mostrar.");
  } else {
    $tweet.fadeOut(200, () => {
      $tweet.html(emoji.replace_unified(tweets[index].text.replace(/\n/mg, "<br/>"))).text();
      $tweet.fadeIn(200);
    });
  }
}

function setupPlaceload() {
  Placeload
      .$("#tweet-text")
      .config({speed: "1s"})
      .line(element => element.width(100).height(15))
      .config({spaceBetween: "7px"})
      .line(element => element.width(100).height(15))
      .config({spaceBetween: "7px"})
      .line(element => element.width(40).height(15)).fold(() => {
  }, () => {
  });
}

function setupEmojiConverter() {
  // noinspection JSUnresolvedFunction
  emoji = new EmojiConvertor();
  emoji.img_set = "twitter";
  emoji.img_sets.twitter.path = "https://raw.githubusercontent.com/iamcal/emoji-data/"
      + "a97b2d2efa64535d6300660eb2cd15ecb584e79e/img-twitter-64/";
}

function getRandomTweets() {
  $.getJSON("tweets", data => {
    tweets = data;
    showTweet();
  });
}

function setUiListeners() {
  $humor.click(() => {
    if (!legendsShownForFirstTime) {
      $legendVote.stop().fadeTo("slow", 1, () =>
          setTimeout(() =>
              $legendVote.stop().fadeTo("slow", 0, () =>
                  $legendVote.css("opacity", "")
              ), 1000)
      );
      legendsShownForFirstTime = true;
    }
  });

  $humor.hover(() => $votesAndToolbox.css("display", ""));

  $notHumor.click(() => {
    vote("x");
    $notHumor.addClass("no-hover");
  });

  $notHumor.on("mousemove mousedown", () => $notHumor.removeClass("no-hover"));

  $vote1.click(() => vote("1"));
  $vote2.click(() => vote("2"));
  $vote3.click(() => vote("3"));
  $vote4.click(() => vote("4"));
  $vote5.click(() => vote("5"));
  $skip.click(() => vote("n"));

  $("#answers button").mouseup(e => $(e.currentTarget).blur());

  $consentForm.submit(e => {
    localStorage.setItem(`consent-prolific-id-${prolificId}`, "done");
    $consent.modal("hide");

    $("#about").modal("show");

    e.preventDefault();
    e.stopPropagation();
  });
}

function vote(voteOption) {
  const oldIndex = index;
  index = (index + 1) % tweets.length;

  const otherIndex = (index + 1) % tweets.length;

  $.post("vote", {
    tweet_id: tweets[oldIndex].id,
    vote: voteOption,
    ignore_tweet_ids: [tweets[index].id, tweets[otherIndex].id],
    is_offensive: $isOffensive.prop("checked"),
  }, tweet => tweets[oldIndex] = tweet, "json");

  showTweet();

  $.mdtoast(toastText(voteOption), {duration: 3000});

  $votesAndToolbox.fadeOut();

  $isOffensive.prop("checked", false);

  if (isAProlificSession) {
    voteCount++;
    updateVoteCount();
  }
}

function toastText(voteOption) {
  if (voteOption === "x") {
    return "Clasificado como no humorístico. ¡Gracias!";
  } else if (voteOption === "n") {
    return "Tweet salteado. ¡Gracias!";
  } else {
    return `Clasificado como ${removeNonWords(voteCodeToText[Number(voteOption)]).toLowerCase()}. ¡Gracias!`;
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
  element.css("left", `${(parseInt(element.css("left")) + translation)}px`);
}

function updateVoteCount() {
  if (voteCount === PROLIFIC_TASK_TWEET_COUNT) {
    $("#finished").modal("show");
  } else {
    voteCount %= PROLIFIC_TASK_TWEET_COUNT;
    $voteCount.text(`Progreso: ${voteCount}/${PROLIFIC_TASK_TWEET_COUNT}`);
  }
}

function setupProlificSessionIfNeeded() {
  if (isAProlificSession) {
    $skip.parent().css("display", "none");
    $("#skip-instructions").css("display", "none");
    $("#optional-participation-instructions").css("display", "none");

    if (localStorage.getItem(`consent-prolific-id-${prolificId}`) !== "done") {
      $("#prolific-id").val(prolificId);
      $consent.modal("show");
      $("#consent-continue").click(() => $.post("prolific-consent"));
    }

    $.getJSON("session-vote-count", count => {
      voteCount = count;
      updateVoteCount();
      $voteCount.css("display", "block");
    });
  }
}
