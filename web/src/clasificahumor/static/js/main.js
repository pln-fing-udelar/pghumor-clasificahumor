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

// Material-style toast notifications (inlined from mdtoast.js): one toast at a time, sliding up from the bottom.
const TOAST_ANIMATE_MS = 250;

function mdtoast(message, {duration = 5000} = {}) {
  document.querySelectorAll(".md-toast").forEach(el => el._hideToast?.());

  const toast = document.createElement("div");
  toast.className = "md-toast mdt-load load";
  const messageEl = document.createElement("div");
  messageEl.className = "mdt-message";
  messageEl.textContent = message;
  toast.appendChild(messageEl);

  let hideTimeout;
  const hide = () => {
    clearTimeout(hideTimeout);
    toast.classList.add("mdt-load", "load");
    document.body.classList.remove("md-toast-open");
    setTimeout(() => toast.remove(), TOAST_ANIMATE_MS);
  };
  toast._hideToast = hide;

  document.body.appendChild(toast);

  setTimeout(() => {
    toast.classList.remove("mdt-load", "load");
    if (duration) {
      hideTimeout = setTimeout(hide, duration);
    }
    document.body.classList.add("md-toast-open");
  }, 10);

  return {hide, element: toast};
}
window.mdtoast = mdtoast;

// Vanilla JS Modal Management (compatible with Bootstrap 3 and Bootstrap 5)
let previouslyFocusedElement = null;

function showModal(modalEl) {
  if (typeof modalEl === "string") {
    modalEl = document.querySelector(modalEl);
  }
  if (!modalEl || modalEl.classList.contains("in") || modalEl.classList.contains("show")) return;

  previouslyFocusedElement = document.activeElement;
  document.body.classList.add("modal-open");

  let backdrop = document.querySelector(".modal-backdrop");
  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.className = "modal-backdrop fade";
    document.body.appendChild(backdrop);
    void backdrop.offsetHeight;
    backdrop.classList.add("in", "show");
  }

  modalEl.style.display = "block";
  void modalEl.offsetHeight;
  modalEl.classList.add("in", "show");
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

  modalEl.classList.remove("in", "show");
  modalEl.removeAttribute("aria-modal");

  const backdrop = document.querySelector(".modal-backdrop");
  if (backdrop) {
    backdrop.classList.remove("in", "show");
  }

  setTimeout(() => {
    modalEl.style.display = "none";
    modalEl.setAttribute("aria-hidden", "true");

    const openModals = document.querySelectorAll(".modal.in, .modal.show");
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
    const toggleBtn = e.target.closest("[data-toggle='modal'], [data-bs-toggle='modal']");
    if (toggleBtn) {
      e.preventDefault();
      const targetSelector =
        toggleBtn.getAttribute("data-bs-target") ||
        toggleBtn.getAttribute("data-target") ||
        toggleBtn.getAttribute("href");
      if (targetSelector && targetSelector !== "#") {
        showModal(targetSelector);
      }
      return;
    }

    const dismissBtn = e.target.closest("[data-dismiss='modal'], [data-bs-dismiss='modal']");
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
      if (modal.getAttribute("data-backdrop") !== "static" && modal.getAttribute("data-bs-backdrop") !== "static") {
        hideModal(modal);
      }
    }
  });

  document.addEventListener("keydown", e => {
    if (e.key === "Escape") {
      const openModals = document.querySelectorAll(".modal.in, .modal.show");
      if (openModals.length > 0) {
        const topModal = openModals[openModals.length - 1];
        if (
          topModal.getAttribute("data-keyboard") !== "false" &&
          topModal.getAttribute("data-bs-keyboard") !== "false"
        ) {
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

// Emoji are shown as Twitter-style images, so they look the same on every device.
const EMOJI_IMAGES_URL =
  "https://raw.githubusercontent.com/iamcal/emoji-data/a97b2d2efa64535d6300660eb2cd15ecb584e79e/img-twitter-64/";

const EMOJI_REGEX = new RegExp(
  [
    String.raw`[#*0-9]\uFE0F?\u20E3`, // Keycaps.
    String.raw`\p{Regional_Indicator}{2}`, // Flags.
    // Pictographs with an optional variation selector or skin tone and tags (like the flag of England), which can be
    // joined with others using "zero width joiners".
    String.raw`\p{Extended_Pictographic}(?:\uFE0F|\p{Emoji_Modifier})?(?:[\u{E0020}-\u{E007E}]+\u{E007F})?` +
      String.raw`(?:\u200D\p{Extended_Pictographic}(?:\uFE0F|\p{Emoji_Modifier})?)*`,
    String.raw`\p{Emoji_Modifier}`, // A lone skin tone.
  ].join("|"),
  "gu"
);
const TEXT_STYLE_EMOJI_REGEX = /^(?!\p{Emoji_Presentation})\p{Emoji}$/u;
const EMOJI_MODIFIER_REGEX = /^\p{Emoji_Modifier}$/u;

// For some emoji that have variants, the image shown is the one of a variant.
const MAN_VARIANT_EMOJI = new Set(
  (
    "1f3c3 1f3c4 1f3ca 1f3cb 1f3cc 1f46e 1f471 1f473 1f477 1f482 1f575 1f647 1f6a3 1f6b4 1f6b5 1f6b6 1f9d6 1f9dc 1f9dd " +
    "1f9de 1f9df 26f9"
  ).split(" ")
);
const WOMAN_VARIANT_EMOJI = new Set(
  "1f46f 1f481 1f486 1f487 1f645 1f646 1f64b 1f64d 1f64e 1f9d7 1f9d8 1f9d9 1f9da 1f9db".split(" ")
);
const OTHER_VARIANT_EMOJI_IMAGES = {
  "1f46a": "1f468-200d-1f469-200d-1f466",
  "1f48f": "1f469-200d-2764-fe0f-200d-1f48b-200d-1f468",
  "1f491": "1f469-200d-2764-fe0f-200d-1f468",
};

// The name of the image of an emoji is its code points in hex, with the variation selector after the ones that need it.
function emojiImageName(emojiText) {
  const characters = [...emojiText].filter(character => character !== "\uFE0F");
  const codePoints = characters.flatMap((character, i) => {
    const codePoint = character.codePointAt(0).toString(16).padStart(4, "0");
    const needsVariationSelector =
      TEXT_STYLE_EMOJI_REGEX.test(character) && !EMOJI_MODIFIER_REGEX.test(characters[i + 1] ?? "");
    return needsVariationSelector ? [codePoint, "fe0f"] : [codePoint];
  });
  const name = codePoints.join("-");

  if (characters.length === 1) {
    if (MAN_VARIANT_EMOJI.has(codePoints[0])) {
      return `${name}-200d-2642-fe0f`;
    } else if (WOMAN_VARIANT_EMOJI.has(codePoints[0])) {
      return `${name}-200d-2640-fe0f`;
    }
  }
  return OTHER_VARIANT_EMOJI_IMAGES[name] ?? name;
}

function emojiToHtml(html) {
  return html.replace(EMOJI_REGEX, emojiText => {
    const name = emojiImageName(emojiText);
    return (
      `<span class="emoji emoji-sizer" role="img" aria-label="${emojiText}" data-codepoints="${name}" ` +
      `style="background-image:url(${EMOJI_IMAGES_URL}${name}.png)"></span>`
    );
  });
}

// Not all emoji have an image (nor is the image always reachable): in that case show the emoji as text.
function showNativeEmojiIfImageIsMissing(element) {
  element.querySelectorAll(".emoji").forEach(emojiEl => {
    const image = new Image();
    image.onerror = () => emojiEl.replaceWith(emojiEl.getAttribute("aria-label"));
    image.src = `${EMOJI_IMAGES_URL}${emojiEl.dataset.codepoints}.png`;
  });
}

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
  setupWhatsAppButton();
  getRandomTweets();
  setUiListeners();
  moveToolboxIfOutside();
  setupProlificSessionIfNeeded();
}

window.sentryOnLoad = () => {
  setupSentry();
};

function setupSentry() {
  if (typeof Sentry !== "undefined" && typeof Sentry.init === "function") {
    Sentry.init({
      dsn: "https://3afb3f9917f44b2a87e6fbb070a8977b@sentry.io/298102",
      sendDefaultPii: true,
      denyUrls: [/https?:\/\/localhost/, /https?:\/\/127\.0\.0\.1/, /https?:\/\/\[::1?]/],
    });
  }
}

// Like the WhatsApp sharing script it replaces, only offer WhatsApp sharing on Android and iPhone.
function setupWhatsAppButton() {
  const userAgent = navigator.userAgent;
  if (/Android|iPhone/i.test(userAgent) && !/iPod|iPad/i.test(userAgent)) {
    document.querySelector(".wa_btn")?.classList.add("wa_btn_visible");
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
    tweetTextEl.innerHTML = emojiToHtml(escapeHtml(tweets[index].text).replace(/\n/mg, "<br/>"));
    showNativeEmojiIfImageIsMissing(tweetTextEl);
  });
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
