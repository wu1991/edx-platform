;(function (define, undefined) {
'use strict';
define([
    'gettext', 'js/edxnotes/views/note_group', 'js/edxnotes/views/tab_panel',
    'js/edxnotes/views/tab_view'
], function (gettext, NoteGroupView, TabPanelView, TabView) {
    var CourseStructureView = TabView.extend({
        PanelConstructor: TabPanelView.extend({
            id: 'structure-panel',
            title: 'Course Structure',

            renderContent: function () {
                var courseStructure = this.collection.getCourseStructure();
                _.each(courseStructure.chapters, function (chapterInfo) {
                    var group = this.getGroup(chapterInfo);
                    _.each(chapterInfo.children, function (location) {
                        var sectionInfo = courseStructure.sections[location],
                            section;
                        if (sectionInfo) {
                            section = group.addChild(sectionInfo);
                            _.each(sectionInfo.children, function (location) {
                                var notes = courseStructure.units[location];
                                if (notes) {
                                    section.addChild(this.getNotes(notes))
                                }
                            }, this);
                        }
                    }, this);
                    group.render().$el.appendTo(this.$el);
                }, this);

                return this;
            },

            getGroup: function (chapter, section) {
                var group = new NoteGroupView({
                    chapter: chapter,
                    section: section
                });
                this.children.push(group);
                return group;
            }
        }),

        tabInfo: {
            name: gettext('Course Structure'),
            identifier: 'view-course-structure',
            icon: 'icon-list-ul'
        }
    });

    return CourseStructureView;
});
}).call(this, define || RequireJS.define);
