define([
    'jquery', 'underscore', 'js/common_helpers/ajax_helpers', 'js/spec/edxnotes/helpers',
    'annotator', 'logger', 'js/edxnotes/views/notes_factory'
], function($, _, AjaxHelpers, Helpers, Annotator, Logger, NotesFactory) {
    'use strict';
    describe('EdxNotes Events Plugin', function() {
        var note = {
            user: 'user-123',
            id: 'note-123',
            text: 'text-123',
            quote: 'quote-123',
            usage_id: 'usage-123'
        };

        beforeEach(function() {
            this.annotator =  NotesFactory.factory(
                $('<div />').get(0), {
                    endpoint: 'http://example.com/'
                }
            );
            spyOn(Logger, 'log');
        });

        afterEach(function () {
            _.invoke(Annotator._instances, 'destroy');
        });

        it('should log edx.course.student_notes.viewed event properly', function() {
            this.annotator.publish('annotationViewerShown', [
                this.annotator.viewer,
                [note, {user: 'user-456', id: 'note-456'}]]
            );
            expect(Logger.log).toHaveBeenCalledWith(
                'edx.course.student_notes.viewed', {
                    'notes': [{'note_id': 'note-123'}, {'note_id': 'note-456'}]
                }
            );
        });

        it('should log edx.course.student_notes.added event properly', function() {
            var requests = AjaxHelpers.requests(this),
                newNote = {
                    user: 'user-123',
                    text: 'text-123',
                    quote: 'quote-123',
                    usage_id: 'usage-123'
                };

            this.annotator.publish('annotationCreated', newNote);
            AjaxHelpers.respondWithJson(requests, note);
            expect(Logger.log).toHaveBeenCalledWith(
                'edx.course.student_notes.added', {
                    'note_id': 'note-123',
                    'note_text': 'text-123',
                    'note_text_truncated': false,
                    'highlighted_content': 'quote-123',
                    'highlighted_content_truncated': false,
                    'component_usage_id': 'usage-123'
                }
            );
        });

        it('should log the edx.course.student_notes.edited event properly', function() {
            var old_note = note,
                new_note = $.extend({}, note, {text: 'text-456'});

            this.annotator.publish('annotationEditorShown', [this.annotator.editor, old_note]);
            expect(this.annotator.plugins.Events.oldNoteText).toBe('text-123');
            this.annotator.publish('annotationUpdated', new_note);
            this.annotator.publish('annotationEditorHidden', [this.annotator.editor, new_note]);

            expect(Logger.log).toHaveBeenCalledWith(
                'edx.course.student_notes.edited', {
                    'note_id': 'note-123',
                    'old_note_text': 'text-123',
                    'old_note_text_truncated': false,
                    'note_text': 'text-456',
                    'note_text_truncated': false,
                    'highlighted_content': 'quote-123',
                    'highlighted_content_truncated': false,
                    'component_usage_id': 'usage-123'
                }
            );
            expect(this.annotator.plugins.Events.oldNoteText).toBeNull();
        });

        it('should log the edx.course.student_notes.deleted event properly', function() {
            this.annotator.publish('annotationDeleted', note);
            expect(Logger.log).toHaveBeenCalledWith(
                'edx.course.student_notes.deleted', {
                    'note_id': 'note-123',
                    'note_text': 'text-123',
                    'note_text_truncated': false,
                    'highlighted_content': 'quote-123',
                    'highlighted_content_truncated': false,
                    'component_usage_id': 'usage-123'
                }
            );
        });

        it('should truncate values of some fields', function() {
            var old_note = $.extend({}, note, {text: Helpers.LONG_TEXT}),
                new_note = $.extend({}, note, {
                    text: Helpers.LONG_TEXT + '123',
                    quote: Helpers.LONG_TEXT + '123'
                });

            this.annotator.publish('annotationEditorShown', [this.annotator.editor, old_note]);
            expect(this.annotator.plugins.Events.oldNoteText).toBe(Helpers.LONG_TEXT);
            this.annotator.publish('annotationUpdated', new_note);
            this.annotator.publish('annotationEditorHidden', [this.annotator.editor, new_note]);

            expect(Logger.log).toHaveBeenCalledWith(
                'edx.course.student_notes.edited', {
                    'note_id': 'note-123',
                    'old_note_text': Helpers.TRUNCATED_TEXT,
                    'old_note_text_truncated': true,
                    'note_text': Helpers.TRUNCATED_TEXT,
                    'note_text_truncated': true,
                    'highlighted_content': Helpers.TRUNCATED_TEXT,
                    'highlighted_content_truncated': true,
                    'component_usage_id': 'usage-123'
                }
            );
            expect(this.annotator.plugins.Events.oldNoteText).toBeNull();
        });
    });
});
