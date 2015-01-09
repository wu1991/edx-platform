;(function (define, undefined) {
'use strict';
define([
    'jquery', 'underscore', 'backbone', 'gettext', 'js/edxnotes/views/visibility_decorator'
], function($, _, Backbone, gettext, EdxnotesVisibilityDecorator) {
    var ToggleNotesView = Backbone.View.extend({
        events: {
            'click .action-toggle-notes': 'toogleHandler'
        },

        errorMessage: gettext("We couldn't <show/hide> your notes. Make sure that you are connected to the Internet, and then try refreshing the page."),

        initialize: function (options) {
            this.visibility = options.visibility;
            this.visibilityUrl = options.visibilityUrl;
            this.checkboxIcon = this.$('.checkbox-icon');
            this.$('.action-toggle-notes').removeClass('is-disabled');
        },

        toogleHandler: function (event) {
            event.preventDefault();
            this.visibility = !this.visibility;
            this.toggleNotes();
            this.sendRequest();
        },

        toggleNotes: function () {
            if (this.visibility) {
                _.each($('.edx-notes-wrapper'), EdxnotesVisibilityDecorator.enableNote);
                this.checkboxIcon.removeClass('icon-check-empty').addClass('icon-check');
            } else {
                EdxnotesVisibilityDecorator.disableNotes();
                this.checkboxIcon.removeClass('icon-check').addClass('icon-check-empty');
            }
        },

        hideErrorMessage: function() {
            this.$('.edx-notes-visibility-error').text('');
        },

        showErrorMessage: function(message) {
            this.$('.edx-notes-visibility-error').text(message);
        },

        sendRequest: function () {
            return $.ajax({
                type: 'PUT',
                url: this.visibilityUrl,
                dataType: 'json',
                data: JSON.stringify({'visibility': this.visibility}),
                success: _.bind(this.onSuccess, this),
                error: _.bind(this.onError, this)
            });
        },

        onSuccess: function () {
            this.hideErrorMessage();
        },

        onError: function () {
            this.showErrorMessage(this.errorMessage);
        }
    });

    return function (visibility, visibilityUrl) {
        return new ToggleNotesView({
            el: $('.edx-notes-visibility').get(0),
            visibility: visibility,
            visibilityUrl: visibilityUrl
        });
    };
});
}).call(this, define || RequireJS.define);
