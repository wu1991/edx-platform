define([
    'js/views/list_item_edit', 'underscore'
],
function(ListItemEdit, _) {
    'use strict';

    var ContentGroupEdit = ListItemEdit.extend({
        tagName: 'div',
        className: 'group-configuration-edit',
        events: {
            'submit': 'setAndClose',
            'click .action-cancel': 'cancel'
        },

        initialize: function() {
            ListItemEdit.prototype.initialize.call(this);
            this.template = this.loadTemplate('content-group-edit');
        },

        getTemplateOptions: function() {
            return {
                name: this.model.escape('name'),
                index: this.model.collection.indexOf(this.model),
                isNew: this.model.isNew(),
                uniqueId: _.uniqueId()
            };
        },

        setValues: function() {
            this.model.set({name: this.$('input').val().trim()});
            return this;
        },

        getSaveableModel: function() {
            return this.model.collection.parents[0];
        }
    });

    return ContentGroupEdit;
});
