define([
    'jquery', 'annotator', 'js/common_helpers/ajax_helpers', 'js/edxnotes/views/visibility_decorator',
    'js/edxnotes/views/toggle_notes_factory', 'js/spec/edxnotes/helpers',
    'js/spec/edxnotes/custom_matchers', 'jasmine-jquery'
], function(
    $, Annotator, AjaxHelpers, VisibilityDecorator, ToggleNotesFactory, Helpers,
    customMatchers
) {
    'use strict';
    describe('EdxNotes ToggleNotesFactory', function() {
        var params = {
            endpoint: '/test_endpoint',
            user: 'a user',
            usageId : 'an usage',
            courseId: 'a course',
            token: Helpers.makeToken(),
            tokenUrl: '/test_token_url'
        };

        beforeEach(function() {
            customMatchers(this);
            loadFixtures(
                'js/fixtures/edxnotes/edxnotes_wrapper.html',
                'js/fixtures/edxnotes/toggle_notes.html'
            );
            VisibilityDecorator.factory(
                document.getElementById('edx-notes-wrapper-123'), params, true
            );
            VisibilityDecorator.factory(
                document.getElementById('edx-notes-wrapper-456'), params, true
            );
            this.toggleNotes = ToggleNotesFactory(true, '/test_url');
            this.button = $('.action-toggle-notes');
            this.icon = this.button.find('.checkbox-icon');
        });

        afterEach(function () {
            VisibilityDecorator._setVisibility(null);
            _.invoke(Annotator._instances, 'destroy');
        });

        it('can toggle notes', function() {
            var requests = AjaxHelpers.requests(this);

            expect(this.button).not.toHaveClass('is-disabled');
            expect(this.icon).toHaveClass('icon-check');
            expect(this.icon).not.toHaveClass('icon-check-empty');

            this.button.click();
            expect(this.icon).toHaveClass('icon-check-empty');
            expect(this.icon).not.toHaveClass('icon-check');
            expect(Annotator._instances).toHaveLength(0);

            AjaxHelpers.expectJsonRequest(requests, 'PUT', '/test_url', {
                'visibility': false
            });
            AjaxHelpers.respondWithJson(requests, {});

            this.button.click();
            expect(this.icon).toHaveClass('icon-check');
            expect(this.icon).not.toHaveClass('icon-check-empty');
            expect(Annotator._instances).toHaveLength(2);

            AjaxHelpers.expectJsonRequest(requests, 'PUT', '/test_url', {
                'visibility': true
            });
            AjaxHelpers.respondWithJson(requests, {});
        });

        it('can handle errors', function() {
            var requests = AjaxHelpers.requests(this),
                errorContainer = $('.edx-notes-visibility-error');

            this.button.click();
            AjaxHelpers.respondWithError(requests);
            expect(errorContainer).toContainText(
                'Cannot save your state. This may be happening because of an error with our server or your internet connection. Try refreshing the page or making sure you are online.'
            );

            this.button.click();
            AjaxHelpers.respondWithJson(requests, {});
            expect(errorContainer).toBeEmpty();
        });
    });
});
