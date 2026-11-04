let homeContent;
let tweetTextEl;
let humorBtn;
let humorContainer;
let votesEl;
let toolboxEl;
let voteBtns;
let vote1Btn;
let vote2Btn;
let vote3Btn;
let vote4Btn;
let vote5Btn;
let legendVoteEls;
let notHumorBtn;
let skipBtn;
let isOffensiveCheckbox;
let voteCountEl;
let consentModal;
let consentForm;
let aboutModal;
let finishedModal;
let emoji;

let legendsShownForFirstTime = false;

const voteCodeToText = {
  1: "Nada gracioso",
  2: "Poco gracioso",
  3: "Regular",
  4: "Bueno",
  5: "¡Buenísimo!",
};

let tweets = [];
let index = 0;

function getParameterByName(name, url = window.location.href) {
  name = name.replace(/[[\]]/g, "\\$&");
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

// Vanilla JS Modal Management
let previouslyFocusedElement = null;

function showModal(modalEl) {
  if (typeof modalEl === "string") {
    modalEl = document.querySelector(modalEl);
  }
  if (!modalEl || modalEl.classList.contains("in")) return;

  previouslyFocusedElement = document.activeElement;
  document.body.classList.add("modal-open");

  let backdrop = document.querySelector(".modal-backdrop");
  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.className = "modal-backdrop fade";
    document.body.appendChild(backdrop);
    void backdrop.offsetHeight;
    backdrop.classList.add("in");
  }

  modalEl.style.display = "block";
  void modalEl.offsetHeight;
  modalEl.classList.add("in");
  modalEl.setAttribute("aria-hidden", "false");
  modalEl.setAttribute("aria-modal", "true");

  const focusable = modalEl.querySelector("button, [href], input, select, textarea, [tabindex]:not([tabindex='-1'])");
  if (focusable && typeof focusable.focus === "function") {
    focusable.focus();
  } else if (typeof modalEl.focus === "function") {
    modalEl.focus();
  }
}

function hideModal(modalEl) {
  if (typeof modalEl === "string") {
    modalEl = document.querySelector(modalEl);
  }
  if (!modalEl) return;

  modalEl.classList.remove("in");
  modalEl.removeAttribute("aria-modal");

  const backdrop = document.querySelector(".modal-backdrop");
  if (backdrop) {
    backdrop.classList.remove("in");
  }

  setTimeout(() => {
    modalEl.style.display = "none";
    modalEl.setAttribute("aria-hidden", "true");

    const openModals = document.querySelectorAll(".modal.in");
    if (openModals.length === 0) {
      document.body.classList.remove("modal-open");
      if (backdrop && backdrop.parentNode) {
        backdrop.parentNode.removeChild(backdrop);
      }
      if (previouslyFocusedElement && typeof previouslyFocusedElement.focus === "function") {
        previouslyFocusedElement.focus();
        previouslyFocusedElement = null;
      }
    }
  }, 150);
}

function setupModalDelegation() {
  document.addEventListener("click", e => {
    const toggleBtn = e.target.closest("[data-toggle='modal']");
    if (toggleBtn) {
      e.preventDefault();
      const targetSelector = toggleBtn.getAttribute("data-target") || toggleBtn.getAttribute("href");
      if (targetSelector && targetSelector !== "#") {
        showModal(targetSelector);
      }
      return;
    }

    const dismissBtn = e.target.closest("[data-dismiss='modal']");
    if (dismissBtn) {
      e.preventDefault();
      const modal = dismissBtn.closest(".modal");
      if (modal) {
        hideModal(modal);
      }
      return;
    }

    if (e.target.classList.contains("modal")) {
      const modal = e.target;
      if (modal.getAttribute("data-backdrop") !== "static") {
        hideModal(modal);
      }
    }
  });

  document.addEventListener("keydown", e => {
    if (e.key === "Escape") {
      const openModals = document.querySelectorAll(".modal.in");
      if (openModals.length > 0) {
        const topModal = openModals[openModals.length - 1];
        if (topModal.getAttribute("data-keyboard") !== "false") {
          hideModal(topModal);
        }
      }
    }
  });
}

function escapeHtml(text) {
  if (text == null) return "";
  return String(text)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
window.escapeHtml = escapeHtml;

function fadeTransition(element, updateFn, duration = 150) {
  if (!element) return;
  element.style.transition = `opacity ${duration}ms ease-in-out`;
  element.style.opacity = "0";
  setTimeout(() => {
    updateFn();
    element.style.opacity = "1";
  }, duration);
}

document.addEventListener("DOMContentLoaded", main);

function main() {
  setupSentry();
  setupElements();
  setupModalDelegation();
  setupPlaceload();
  setupEmojiConverter();
  getRandomTweets();
  setUiListeners();
  moveToolboxIfOutside();
  setupProlificSessionIfNeeded();
}

function setupSentry() {
  if (typeof Raven !== "undefined") {
    // The following key is public.
    Raven.config("https://3afb3f9917f44b2a87e6fbb070a8977b@sentry.io/298102", {
      ignoreUrls: ["localhost", "127.0.0.1"],
    }).install();
  }
}

function setupElements() {
  homeContent = document.getElementById("home-content");
  tweetTextEl = document.getElementById("tweet-text");
  humorBtn = document.getElementById("humor");
  humorContainer = document.getElementById("humor-container");
  votesEl = document.getElementById("votes");
  toolboxEl = document.getElementById("toolbox");
  voteBtns = document.querySelectorAll(".vote");
  vote1Btn = document.getElementById("vote-1");
  vote2Btn = document.getElementById("vote-2");
  vote3Btn = document.getElementById("vote-3");
  vote4Btn = document.getElementById("vote-4");
  vote5Btn = document.getElementById("vote-5");
  legendVoteEls = document.querySelectorAll(".legend-vote");
  notHumorBtn = document.getElementById("not-humor");
  skipBtn = document.getElementById("skip");
  isOffensiveCheckbox = document.getElementById("is-offensive");
  voteCountEl = document.getElementById("vote-count");
  consentModal = document.getElementById("consent");
  consentForm = document.querySelector("#consent form");
  aboutModal = document.getElementById("about");
  finishedModal = document.getElementById("finished");
}

function showTweet() {
  if (tweets.length === 0) {
    console.error("No hay tweets para mostrar.");
    return;
  }
  fadeTransition(tweetTextEl, () => {
    tweetTextEl.innerHTML = emoji.replace_unified(escapeHtml(tweets[index].text).replace(/\n/mg, "<br/>"));
  });
}

function setupPlaceload() {
  Placeload
    .$("#tweet-text")
    .config({speed: "1s"})
    .line(element => element.width(100).height(15))
    .config({spaceBetween: "7px"})
    .line(element => element.width(100).height(15))
    .config({spaceBetween: "7px"})
    .line(element => element.width(40).height(15))
    .fold(
      () => {},
      () => {}
    );
}

function setupEmojiConverter() {
  emoji = new EmojiConvertor();
  emoji.img_set = "twitter";
  emoji.img_sets.twitter.path =
    "https://raw.githubusercontent.com/iamcal/emoji-data/a97b2d2efa64535d6300660eb2cd15ecb584e79e/img-twitter-64/";
}

async function getRandomTweets() {
  try {
    const res = await fetch("tweets");
    if (res.ok) {
      tweets = await res.json();
      showTweet();
    }
  } catch (err) {
    console.error("Failed to load tweets:", err);
  }
}

function setUiListeners() {
  humorBtn.addEventListener("click", () => {
    if (!legendsShownForFirstTime) {
      legendVoteEls.forEach(el => {
        el.style.opacity = "1";
      });
      setTimeout(() => {
        legendVoteEls.forEach(el => {
          el.style.opacity = "";
        });
      }, 1000);
      legendsShownForFirstTime = true;
    }
  });

  humorContainer.addEventListener("mouseenter", () => {
    votesEl.style.display = "";
    toolboxEl.style.display = "";
  });

  notHumorBtn.addEventListener("click", () => {
    vote("x");
    notHumorBtn.classList.add("no-hover");
  });

  ["mousemove", "mousedown"].forEach(evt => {
    notHumorBtn.addEventListener(evt, () => notHumorBtn.classList.remove("no-hover"));
  });

  vote1Btn.addEventListener("click", () => vote("1"));
  vote2Btn.addEventListener("click", () => vote("2"));
  vote3Btn.addEventListener("click", () => vote("3"));
  vote4Btn.addEventListener("click", () => vote("4"));
  vote5Btn.addEventListener("click", () => vote("5"));
  skipBtn.addEventListener("click", () => vote("n"));

  document.querySelectorAll("#answers button").forEach(btn => {
    btn.addEventListener("mouseup", e => e.currentTarget.blur());
  });

  if (consentForm) {
    consentForm.addEventListener("submit", e => {
      localStorage.setItem(`consent-prolific-id-${prolificId}`, "done");
      hideModal(consentModal);
      showModal(aboutModal);

      e.preventDefault();
      e.stopPropagation();
    });
  }
}

function vote(voteOption) {
  if (tweets.length === 0) return;

  const oldIndex = index;
  index = (index + 1) % tweets.length;
  const otherIndex = (index + 1) % tweets.length;

  const payload = {
    tweet_id: tweets[oldIndex].id,
    vote: voteOption,
    ignore_tweet_ids: [tweets[index]?.id, tweets[otherIndex]?.id].filter(Boolean),
    is_offensive: Boolean(isOffensiveCheckbox?.checked),
  };

  fetch("vote", {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload),
  })
    .then(res => res.json())
    .then(tweet => {
      tweets[oldIndex] = tweet;
    })
    .catch(err => {
      console.error("Failed to submit vote:", err);
    });

  showTweet();

  mdtoast(toastText(voteOption), {duration: 3000});

  votesEl.style.display = "none";
  toolboxEl.style.display = "none";

  if (isOffensiveCheckbox) {
    isOffensiveCheckbox.checked = false;
  }

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
  if (!toolboxEl) return;
  const rect = toolboxEl.getBoundingClientRect();
  if (rect.x < 0) {
    const translation = -rect.x + 10;
    addPxToLeft(toolboxEl, translation);
    addPxToLeft(vote1Btn, translation);
    addPxToLeft(vote2Btn, translation);
    addPxToLeft(vote3Btn, translation);
    addPxToLeft(vote4Btn, translation);
    addPxToLeft(vote5Btn, translation);
  }
}

function addPxToLeft(element, translation) {
  if (!element) return;
  const currentLeft = parseInt(window.getComputedStyle(element).left, 10) || 0;
  element.style.left = `${currentLeft + translation}px`;
}

function updateVoteCount() {
  if (voteCount === PROLIFIC_TASK_TWEET_COUNT) {
    showModal(finishedModal);
  } else {
    voteCount %= PROLIFIC_TASK_TWEET_COUNT;
    if (voteCountEl) {
      voteCountEl.textContent = `Progreso: ${voteCount}/${PROLIFIC_TASK_TWEET_COUNT}`;
    }
  }
}

async function setupProlificSessionIfNeeded() {
  if (isAProlificSession) {
    if (skipBtn && skipBtn.parentElement) {
      skipBtn.parentElement.style.display = "none";
    }
    const skipInstructions = document.getElementById("skip-instructions");
    if (skipInstructions) {
      skipInstructions.style.display = "none";
    }
    const optInstructions = document.getElementById("optional-participation-instructions");
    if (optInstructions) {
      optInstructions.style.display = "none";
    }

    if (localStorage.getItem(`consent-prolific-id-${prolificId}`) !== "done") {
      const prolificIdInput = document.getElementById("prolific-id");
      if (prolificIdInput) {
        prolificIdInput.value = prolificId;
      }
      showModal(consentModal);
      const consentContinueBtn = document.getElementById("consent-continue");
      if (consentContinueBtn) {
        consentContinueBtn.addEventListener("click", () => {
          fetch("prolific-consent", {method: "POST"});
        });
      }
    }

    try {
      const res = await fetch("session-vote-count");
      if (res.ok) {
        voteCount = await res.json();
        updateVoteCount();
        if (voteCountEl) {
          voteCountEl.style.display = "block";
        }
      }
    } catch (err) {
      console.error("Failed to fetch session vote count:", err);
    }
  }
}
