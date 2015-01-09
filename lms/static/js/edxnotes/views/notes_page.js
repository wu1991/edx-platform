;(function (define, undefined) {
'use strict';
define([
    'backbone', 'js/edxnotes/collections/tabs', 'js/edxnotes/views/tabs_list',
    'js/edxnotes/views/tabs/recent_activity', 'js/edxnotes/views/tabs/search_results'
], function (
    Backbone, TabsCollection, TabsListView, RecentActivityView, SearchResultsView
) {
    var NotesPageView = Backbone.View.extend({
        initialize: function (options) {
            this.options = options;
            this.tabsCollection = new TabsCollection();
            this.recentActivityView = new RecentActivityView({
                el: this.el,
                collection: this.collection,
                tabsCollection: this.tabsCollection
            });

            this.searchResultsView = new SearchResultsView({
                el: this.el,
                tabsCollection: this.tabsCollection,
                user: this.options.user,
                courseId: this.options.courseId,
                debug: this.options.debug,
                createTabOnInitialization: false
            });

            this.tabsView = new TabsListView({collection: this.tabsCollection});
            this.$('.edx-notes-page-views')
                .append(this.tabsView.render().$el)
                .removeClass('is-hidden');
        }
    });

    return NotesPageView;
});
}).call(this, define || RequireJS.define);
