;(function (define) {
'use strict';
define(['backbone', 'underscore.string'], function (Backbone) {
    var NoteModel = Backbone.Model.extend({
        defaults: {
            'id': null,
            'created': null,
            'updated': null,
            'user': null,
            'usage_id': null,
            'course_id': null,
            'text': null,
            'quote': '',
            'unit': {
                'display_name': null,
                'url': null
            },
            'ranges': [],
            // Flag indicating current state of the note: expanded or collapsed.
            'is_expanded': false,
            // Flag indicating whether `More` link should be shown.
            'show_link': false
        },

        textSize: 300,

        initialize: function () {
            if (this.get('quote').length > this.textSize) {
                this.set('show_link', true);
            }
        },

        getNoteText: function () {
            var message = this.get('quote');

            if (!this.get('is_expanded') && this.get('show_link')) {
                message = _.str.prune(message, this.textSize);
            }

            return message;
        }

    });

    return NoteModel;
});
}).call(this, define || RequireJS.define);
