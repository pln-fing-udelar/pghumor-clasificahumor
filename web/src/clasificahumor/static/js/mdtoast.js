// Modified version by Santiago Castro with a fix when hiding alerts too fast.
// Rewritten in vanilla JavaScript (no jQuery dependency).

/* -- DO NOT REMOVE --
 * Material Toast plugin v1
 *
 * Author: Dionlee Uy
 * Email: dionleeuy@gmail.com
 *
 * Date: Tue Apr 4 2017
 * -- DO NOT REMOVE --
 */
(function (root, factory) {
  if (typeof define === "function" && define.amd) {
    define([], factory);
  } else if (typeof exports === "object") {
    module.exports = factory();
  } else {
    const toastFn = factory();
    root.mdtoast = toastFn;
    if (typeof root.$ !== "undefined") {
      root.$.mdtoast = toastFn;
    }
  }
})(typeof window !== "undefined" ? window : this, function () {
  "use strict";

  function extend(target, ...sources) {
    for (const source of sources) {
      if (source && typeof source === "object") {
        for (const key of Object.keys(source)) {
          target[key] = source[key];
        }
      }
    }
    return target;
  }

  const MDToast = function (message, options) {
    this.animateTime = 250;
    this.options = extend({}, mdtoast.defaults, options);
    this.toastOpenClass = "md-toast-open";
    this.toastModalClass = "md-toast-modal";
    this.toastTimeout = null;

    this.toast = document.createElement("div");
    this.toast.className = "md-toast mdt-load load";
    if (this.options.type && this.options.type !== "default") {
      this.toast.classList.add(this.options.type);
    }

    const messageDiv = document.createElement("div");
    messageDiv.className = "mdt-message";
    messageDiv.innerHTML = message;
    this.toast.appendChild(messageDiv);

    if (this.options.interaction) {
      const that = this;
      this.action = document.createElement("button");
      this.action.className = "mdt-action action";
      this.action.textContent = this.options.actionText;
      this.action.addEventListener("click", () => {
        if (typeof that.options.action === "function") {
          that.options.action(that);
        }
      });
      this.toast.appendChild(this.action);
    }

    this.toast._mdtoast = this;

    if (!this.options.init) {
      this.show();
    }
  };

  MDToast.prototype = {
    show: function () {
      const that = this;
      const callbacks = that.options.callbacks;
      const doc = document.body;

      if (that.toast.parentNode) return;

      const existingToasts = document.querySelectorAll(".md-toast");
      existingToasts.forEach(el => {
        if (el._mdtoast && typeof el._mdtoast.hide === "function") {
          el._mdtoast.hide();
        }
      });

      doc.appendChild(that.toast);

      setTimeout(() => {
        that.toast.classList.remove("mdt-load");
        that.toast.classList.remove("load");

        setTimeout(() => {
          if (callbacks && typeof callbacks.shown === "function") {
            callbacks.shown(that);
          }
        }, that.animateTime);

        if (that.options.interaction) {
          if (that.options.interactionTimeout) {
            that.toastTimeout = setTimeout(() => {
              that.hide();
            }, that.options.interactionTimeout);
          }
        } else if (that.options.duration) {
          that.toastTimeout = setTimeout(() => {
            that.hide();
          }, that.options.duration);
        }

        doc.classList.add(that.toastOpenClass);
        if (that.options.modal) {
          doc.classList.add(that.toastModalClass);
        }
      }, 10);
    },
    hide: function () {
      const that = this;
      const callbacks = that.options.callbacks;
      const doc = document.body;

      clearTimeout(that.toastTimeout);

      that.toast.classList.add("mdt-load");
      that.toast.classList.add("load");
      doc.classList.remove(that.toastOpenClass);
      doc.classList.remove(that.toastModalClass);

      setTimeout(() => {
        if (that.toast.parentNode) {
          that.toast.parentNode.removeChild(that.toast);
        }
        if (callbacks && typeof callbacks.hidden === "function") {
          callbacks.hidden();
        }
      }, that.animateTime);
    },
  };

  function mdtoast(message, options) {
    return new MDToast(message, typeof options === "object" ? options : {});
  }

  mdtoast.defaults = {
    init: false,
    duration: 5000,
    type: "default",
    modal: false,
    interaction: false,
    interactionTimeout: null,
    actionText: "OK",
    action: data => {
      data.hide();
    },
    callbacks: {},
  };

  mdtoast.type = {
    INFO: "info",
    ERROR: "error",
    WARNING: "warning",
    SUCCESS: "success",
  };

  mdtoast.Constructor = MDToast;

  return mdtoast;
});
