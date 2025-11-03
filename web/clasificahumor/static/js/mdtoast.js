// Modified version by Santiago Castro with a fix when hiding alerts too fast.

/* -- DO NOT REMOVE --
 * jQuery Material Toast plugin v1
 * 
 * Author: Dionlee Uy
 * Email: dionleeuy@gmail.com
 *
 * Date: Tue Apr 4 2017
 *
 * @requires jQuery
 * -- DO NOT REMOVE --
 */
if (typeof jQuery === 'undefined') {
    throw new Error('MDToast: This plugin requires jQuery');
}
+($ => {
    const MDToast = function (message, options) {
        this.animateTime = 250;
        this.options = options;
        this.toastOpenClass = "md-toast-open";
        this.toastModalClass = "md-toast-modal";
        this.TOAST_DATA = "dmu-md-toast";

        this.toast = $('<div class="md-toast mdt-load"></div>');
        this.action = $('<button class="mdt-action"></button>');

        this.toastTimeout = null;

        this.toast.addClass(options.type).append('<div class="mdt-message">' + message + '</div>');

        if (options.interaction) {
            const that = this;
            this.action.text(options.actionText)
                .on('click', () => {
                    if (options.action) options.action(that);
                });
            this.toast.append(this.action);
        }

        if (!options.init) this.show();
    };

    MDToast.prototype = {
        show: function () {
            const that = this,
                callbacks = that.options.callbacks,
                existingToast = $('.md-toast'),
                doc = $('body');

            if (that.toast.is(':visible')) return;

            that.toast.data(that.TOAST_DATA, that).appendTo(doc);

            setTimeout(() => {
                that.toast.removeClass('mdt-load');

                if (existingToast.length > 0) {
                    existingToast.each(function () {
                        const ex_toast = $(this).data(that.TOAST_DATA);

                        if (ex_toast !== undefined) {
                            ex_toast.hide();
                        }
                    });
                }

                setTimeout(() => {
                        // noinspection JSUnresolvedVariable
                        if (callbacks && callbacks.shown) {
                            // noinspection JSUnresolvedFunction
                            callbacks.shown(that);
                        }
                    },
                    that.animateTime);

                if (that.options.interaction) {
                    if (that.options.interactionTimeout)
                        that.toastTimeout = setTimeout(() => {
                            that.hide();
                        }, that.options.interactionTimeout);
                } else if (that.options.duration) {
                    that.toastTimeout = setTimeout(() => {
                        that.hide();
                    }, that.options.duration);
                }


                doc.addClass(that.toastOpenClass);

                if (that.options.modal) doc.addClass(that.toastModalClass);
            }, 10);
        },
        hide: function () {
            const that = this,
                callbacks = that.options.callbacks;
            const doc = $('body');

            clearTimeout(that.toastTimeout);

            that.toast.addClass('mdt-load');
            doc.removeClass(that.toastOpenClass).removeClass(that.toastModalClass);
            setTimeout(() => {
                that.toast.remove();
                if (callbacks && callbacks.hidden) callbacks.hidden();
            }, that.animateTime);
        }
    };

    $.mdtoast = (message, options) => new MDToast(message, $.extend({}, $.mdtoast.defaults, null, typeof options === 'object' && options));

    $.mdtoast.defaults = {
        init: false,				// true if initialize only, false to automatically show toast after initialization.
        duration: 5000,				// duration ot toast message.
        type: 'default',			// type of toast to display (can also be info, error, warning, success)
        modal: false,				// true if you want to disable pointer events when toast is shown
        interaction: false,			// determines if toast requires user interaction to dismiss
        interactionTimeout: null,	// if requires interaction, set the value for automatic dismissal of toast (e.g. 2000 -> 2 seconds)
        actionText: 'OK',			// if requires interaction, set the value like 'UNDO'
        action: data => {	// callback action for the user interaction, hides toast by default
            data.hide();
        },
        callbacks: {}				// callback object for toast; contains hidden() and shown()
    };

    $.mdtoast.type = {
        INFO: 'info',
        ERROR: 'error',
        WARNING: 'warning',
        SUCCESS: 'success'
    };

    $.mdtoast.Constructor = MDToast;
})(jQuery);
