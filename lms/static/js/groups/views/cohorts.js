var edx = edx || {};

(function($, _, Backbone, gettext, interpolate_text, CohortModel, CohortEditorView, CohortFormView,
          NotificationModel, NotificationView, FileUploaderView) {
    'use strict';

    var hiddenClass = 'is-hidden',
        disabledClass = 'is-disabled';

    edx.groups = edx.groups || {};

    edx.groups.CohortsView = Backbone.View.extend({
        events : {
            'change .cohort-select': 'onCohortSelected',
            'click .action-create': 'showAddCohortForm',
            'click .cohort-management-add-form .action-save': 'saveAddCohortForm',
            'click .cohort-management-add-form .action-cancel': 'cancelAddCohortForm',
            'click .link-cross-reference': 'showSection',
            'click .toggle-cohort-management-secondary': 'showCsvUpload'
        },

        initialize: function(options) {
            var model = this.model;

            this.template = _.template($('#cohorts-tpl').text());
            this.selectorTemplate = _.template($('#cohort-selector-tpl').text());
            this.context = options.context;
            this.contentGroups = options.contentGroups;
            model.on('sync', this.onSync, this);

            // Update cohort counts when the user clicks back on the membership tab
            // (for example, after uploading a csv file of cohort assignments and then
            // checking results on data download tab).
            $(this.getSectionCss('membership')).click(function () {
                model.fetch();
            });
        },

        render: function() {
            this.$el.html(this.template({
                cohorts: this.model.models
            }));
            this.onSync();
            return this;
        },

        renderSelector: function(selectedCohort) {
            this.$('.cohort-select').html(this.selectorTemplate({
                cohorts: this.model.models,
                selectedCohort: selectedCohort
            }));
        },

        onSync: function(model, response, options) {
            var selectedCohort = this.lastSelectedCohortId && this.model.get(this.lastSelectedCohortId),
                hasCohorts = this.model.length > 0,
                cohortNavElement = this.$('.cohort-management-nav'),
                additionalCohortControlElement = this.$('.wrapper-cohort-supplemental'),
                isModelUpdate;
            isModelUpdate = function() {
                // Distinguish whether this is a sync event for just one model, or if it is for
                // an entire collection.
                return options && options.patch && response.hasOwnProperty('user_partition_id');
            };
            this.hideAddCohortForm();
            if (isModelUpdate()) {
                // Refresh the selector in case the model's name changed
                this.renderSelector(selectedCohort);
            } else if (hasCohorts) {
                cohortNavElement.removeClass(hiddenClass);
                additionalCohortControlElement.removeClass(hiddenClass);
                this.renderSelector(selectedCohort);
                if (selectedCohort) {
                    this.showCohortEditor(selectedCohort);
                }
            } else {
                cohortNavElement.addClass(hiddenClass);
                additionalCohortControlElement.addClass(hiddenClass);
                this.showNotification({
                    type: 'warning',
                    title: gettext('You currently have no cohorts configured'),
                    actionText: gettext('Add Cohort'),
                    actionClass: 'action-create',
                    actionIconClass: 'fa-plus'
                });
            }
        },

        getSelectedCohort: function() {
            var id = this.$('.cohort-select').val();
            return id && this.model.get(parseInt(id));
        },

        onCohortSelected: function(event) {
            event.preventDefault();
            var selectedCohort = this.getSelectedCohort();
            this.lastSelectedCohortId = selectedCohort.get('id');
            this.showCohortEditor(selectedCohort);
        },

        showCohortEditor: function(cohort) {
            this.removeNotification();
            if (this.editor) {
                this.editor.setCohort(cohort);
            } else {
                this.editor = new CohortEditorView({
                    el: this.$('.cohort-management-group'),
                    model: cohort,
                    cohorts: this.model,
                    contentGroups: this.contentGroups,
                    context: this.context
                });
                this.editor.render();
            }
        },

        showNotification: function(options, beforeElement) {
            var model = new NotificationModel(options);
            this.removeNotification();
            this.notification = new NotificationView({
                model: model
            });
            this.notification.render();
            if (!beforeElement) {
                beforeElement = this.$('.cohort-management-group');
            }
            beforeElement.before(this.notification.$el);
        },

        removeNotification: function() {
            if (this.notification) {
                this.notification.remove();
            }
            if (this.cohortFormView) {
                this.cohortFormView.removeNotification();
            }
        },

        showAddCohortForm: function(event) {
            var newCohort;
            event.preventDefault();
            this.removeNotification();
            newCohort = new CohortModel();
            newCohort.url = this.model.url;
            this.cohortFormView = new CohortFormView({
                model: newCohort,
                contentGroups: this.contentGroups,
                context: this.context
            });
            this.cohortFormView.render();
            this.$('.cohort-management-add-form').append(this.cohortFormView.$el);
            this.setCohortEditorVisibility(false);
        },

        hideAddCohortForm: function() {
            this.setCohortEditorVisibility(true);
            if (this.cohortFormView) {
                this.cohortFormView.remove();
                this.cohortFormView = null;
            }
        },

        setCohortEditorVisibility: function(showEditor) {
            if (showEditor) {
                this.$('.cohort-management-group').removeClass(hiddenClass);
                this.$('.cohort-management-nav').removeClass(disabledClass).attr('aria-disabled', false);
            } else {
                this.$('.cohort-management-group').addClass(hiddenClass);
                this.$('.cohort-management-nav').addClass(disabledClass).attr('aria-disabled', true);
            }
        },

        saveAddCohortForm: function(event) {
            var self = this,
                newCohort = this.cohortFormView.model;
            event.preventDefault();
            this.removeNotification();
            this.cohortFormView.saveForm()
                .done(function() {
                    self.lastSelectedCohortId = newCohort.id;
                    self.model.fetch().done(function() {
                        self.showNotification({
                            type: 'confirmation',
                            title: interpolate_text(
                                gettext('The {cohortGroupName} cohort has been created. You can manually add students to this cohort below.'),
                                {cohortGroupName: newCohort.get('name')}
                            )
                        });
                    });
                });
        },

        cancelAddCohortForm: function(event) {
            event.preventDefault();
            this.removeNotification();
            this.onSync();
        },

        showSection: function(event) {
            event.preventDefault();
            var section = $(event.currentTarget).data("section");
            $(this.getSectionCss(section)).click();
            $(window).scrollTop(0);
        },

        showCsvUpload: function(event) {
            event.preventDefault();

            $(event.currentTarget).addClass(hiddenClass);
            var uploadElement = this.$('.csv-upload').removeClass(hiddenClass);

            if (!this.fileUploaderView) {
                this.fileUploaderView = new FileUploaderView({
                    el: uploadElement,
                    title: gettext("Assign students to cohorts by uploading a CSV file."),
                    inputLabel: gettext("Choose a .csv file"),
                    inputTip: gettext("Only properly formatted .csv files will be accepted."),
                    submitButtonText: gettext("Upload File and Assign Students"),
                    extensions: ".csv",
                    url: this.context.uploadCohortsCsvUrl,
                    successNotification: function (file, event, data) {
                        var message = interpolate_text(gettext(
                            "Your file '{file}' has been uploaded. Allow a few minutes for processing."
                        ), {file: file});
                        return new NotificationModel({
                            type: "confirmation",
                            title: message
                        });
                    }
                }).render();
            }
        },

        getSectionCss: function (section) {
            return ".instructor-nav .nav-item a[data-section='" + section + "']";
        }
    });
}).call(this, $, _, Backbone, gettext, interpolate_text, edx.groups.CohortModel, edx.groups.CohortEditorView,
    edx.groups.CohortFormView, NotificationModel, NotificationView, FileUploaderView);
