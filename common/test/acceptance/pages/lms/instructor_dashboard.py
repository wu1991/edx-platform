# -*- coding: utf-8 -*-
"""
Instructor (2) dashboard page.
"""

from bok_choy.page_object import PageObject
from .course_page import CoursePage
import os
from bok_choy.promise import EmptyPromise
from ...tests.helpers import select_option_by_text, get_selected_option_text, get_options


class InstructorDashboardPage(CoursePage):
    """
    Instructor dashboard, where course staff can manage a course.
    """
    url_path = "instructor"

    def is_browser_on_page(self):
        return self.q(css='div.instructor-dashboard-wrapper-2').present

    def select_membership(self):
        """
        Selects the membership tab and returns the MembershipSection
        """
        self.q(css='a[data-section=membership]').first.click()
        membership_section = MembershipPage(self.browser)
        membership_section.wait_for_page()
        return membership_section

    def select_data_download(self):
        """
        Selects the data download tab and returns a DataDownloadPage.
        """
        self.q(css='a[data-section=data_download]').first.click()
        data_download_section = DataDownloadPage(self.browser)
        data_download_section.wait_for_page()
        return data_download_section

    @staticmethod
    def get_asset_path(file_name):
        """
        Returns the full path of the file to upload.
        These files have been placed in edx-platform/common/test/data/uploads/
        """

        # Separate the list of folders in the path reaching to the current file,
        # e.g.  '... common/test/acceptance/pages/lms/instructor_dashboard.py' will result in
        #       [..., 'common', 'test', 'acceptance', 'pages', 'lms', 'instructor_dashboard.py']
        folders_list_in_path = __file__.split(os.sep)

        # Get rid of the last 4 elements: 'acceptance', 'pages', 'lms', and 'instructor_dashboard.py'
        # to point to the 'test' folder, a shared point in the path's tree.
        folders_list_in_path = folders_list_in_path[:-4]

        # Append the folders in the asset's path
        folders_list_in_path.extend(['data', 'uploads', file_name])

        # Return the joined path of the required asset.
        return os.sep.join(folders_list_in_path)


class MembershipPage(PageObject):
    """
    Membership section of the Instructor dashboard.
    """
    url = None

    def is_browser_on_page(self):
        return self.q(css='a[data-section=membership].active-section').present

    def select_auto_enroll_section(self):
        """
        Returns the MembershipPageAutoEnrollSection page object.
        """
        return MembershipPageAutoEnrollSection(self.browser)

    def select_cohort_management_section(self):
        """
        Returns the MembershipPageCohortManagementSection page object.
        """
        return MembershipPageCohortManagementSection(self.browser)


class MembershipPageCohortManagementSection(PageObject):
    """
    The cohort management subsection of the Membership section of the Instructor dashboard.
    """
    url = None
    csv_browse_button_selector_css = '.csv-upload #file-upload-form-file'
    csv_upload_button_selector_css = '.csv-upload #file-upload-form-submit'
    content_group_selector_css = 'select.input-cohort-group-association'
    no_content_group_button_css = '.cohort-management-details-association-course input.radio-no'
    select_content_group_button_css = '.cohort-management-details-association-course input.radio-yes'

    def is_browser_on_page(self):
        return self.q(css='.cohort-management.membership-section').present

    def _bounded_selector(self, selector):
        """
        Return `selector`, but limited to the cohort management context.
        """
        return '.cohort-management.membership-section {}'.format(selector)

    def _get_cohort_options(self):
        """
        Returns the available options in the cohort dropdown, including the initial "Select a cohort group".
        """
        return self.q(css=self._bounded_selector("#cohort-select option"))

    def _cohort_name(self, label):
        """
        Returns the name of the cohort with the count information excluded.
        """
        return label.split(' (')[0]

    def _cohort_count(self, label):
        """
        Returns the count for the cohort (as specified in the label in the selector).
        """
        return int(label.split(' (')[1].split(')')[0])

    def get_cohorts(self):
        """
        Returns, as a list, the names of the available cohorts in the drop-down, filtering out "Select a cohort group".
        """
        return [
            self._cohort_name(opt.text)
            for opt in self._get_cohort_options().filter(lambda el: el.get_attribute('value') != "")
        ]

    def get_selected_cohort(self):
        """
        Returns the name of the selected cohort.
        """
        EmptyPromise(
            lambda: len(self._get_cohort_options().results) > 0,
            "Waiting for cohort selector to populate"
        ).fulfill()
        return self._cohort_name(
            self._get_cohort_options().filter(lambda el: el.is_selected()).first.text[0]
        )

    def get_selected_cohort_count(self):
        """
        Returns the number of users in the selected cohort.
        """
        return self._cohort_count(
            self._get_cohort_options().filter(lambda el: el.is_selected()).first.text[0]
        )

    def select_cohort(self, cohort_name):
        """
        Selects the given cohort in the drop-down.
        """
        EmptyPromise(
            lambda: cohort_name in self.get_cohorts(),
            "Waiting for cohort selector to populate"
        ).fulfill()
        # Note: can't use Select to select by text because the count is also included in the displayed text.
        self._get_cohort_options().filter(
            lambda el: self._cohort_name(el.text) == cohort_name
        ).first.click()

    def add_cohort(self, cohort_name, content_group=None):
        """
        Adds a new manual cohort with the specified name.
        If a content group should also be associated, the name of the content group should be specified.
        """
        create_buttons = self.q(css=self._bounded_selector(".action-create"))
        # There are 2 create buttons on the page. The first one is only visible when a cohort
        # already exists. If it is visible, click on it. Otherwise try the second.
        if create_buttons.first.visible:
            create_buttons.first.click()
        else:
            create_buttons.results[1].click()

        textinput = self.q(css=self._bounded_selector("#cohort-name")).results[0]
        textinput.send_keys(cohort_name)
        if content_group:
            self._select_associated_content_group(content_group)
        self.q(css=self._bounded_selector("div.form-actions .action-save")).first.click()

    def get_cohort_group_setup(self):
        """
        Returns the description of the current cohort
        """
        return self.q(css=self._bounded_selector('.cohort-management-group-setup .setup-value')).first.text[0]

    def select_edit_settings(self):
        self.q(css=self._bounded_selector(".action-edit")).first.click()

    def add_students_to_selected_cohort(self, users):
        """
        Adds a list of users (either usernames or email addresses) to the currently selected cohort.
        """
        textinput = self.q(css=self._bounded_selector("#cohort-management-group-add-students")).results[0]
        for user in users:
            textinput.send_keys(user)
            textinput.send_keys(",")
        self.q(css=self._bounded_selector("div.cohort-management-group-add .action-primary")).first.click()

    def get_cohort_student_input_field_value(self):
        """
        Returns the contents of the input field where students can be added to a cohort.
        """
        return self.q(
            css=self._bounded_selector("#cohort-management-group-add-students")
        ).results[0].get_attribute("value")

    def select_studio_group_settings(self):
        """
        When no content groups have been defined, a messages appears with a link
        to go to Studio group settings. This method assumes the link is visible and clicks it.
        """
        return self.q(css=self._bounded_selector("a.link-to-group-settings")).first.click()

    def get_all_content_groups(self):
        """
        Returns all the content groups available for associating with the cohort currently being edited.
        """
        selector_query = self.q(css=self._bounded_selector(self.content_group_selector_css))
        return [
            option.text for option in get_options(selector_query) if option.text != "Not selected"
        ]

    def get_cohort_associated_content_group(self):
        """
        Returns the content group associated with the cohort currently being edited.
        If no content group is associated, returns None.
        """
        self.select_cohort_settings()
        radio_button = self.q(css=self._bounded_selector(self.no_content_group_button_css)).results[0]
        if radio_button.is_selected():
            return None
        return get_selected_option_text(self.q(css=self._bounded_selector(self.content_group_selector_css)))

    def set_cohort_associated_content_group(self, content_group=None, select_settings=True):
        """
        Sets the content group associated with the cohort currently being edited.
        If content_group is None, un-links the cohort group from any content group.
        Presses Save to update the cohort's settings.
        """
        if select_settings:
            self.select_cohort_settings()
        if content_group is None:
            self.q(css=self._bounded_selector(self.no_content_group_button_css)).first.click()
        else:
            self._select_associated_content_group(content_group)
        self.q(css=self._bounded_selector("div.form-actions .action-save")).first.click()

    def _select_associated_content_group(self, content_group):
        """
        Selects the specified content group from the selector. Assumes that content_group is not None.
        """
        self.select_content_group_radio_button()
        select_option_by_text(
            self.q(css=self._bounded_selector(self.content_group_selector_css)), content_group
        )

    def select_content_group_radio_button(self):
        """
        Clicks the radio button for "No Content Group" association.
        Returns whether or not the radio button is in the selected state after the click.
        """
        radio_button = self.q(css=self._bounded_selector(self.select_content_group_button_css)).results[0]
        radio_button.click()
        return radio_button.is_selected()

    def select_cohort_settings(self):
        """
        Selects the settings tab for the cohort currently being edited.
        """
        self.q(css=self._bounded_selector(".cohort-management-settings li.tab-settings>a")).first.click()

    # pylint: disable=redefined-builtin
    def get_cohort_settings_messages(self, type="confirmation", wait_for_messages=True):
        """
        Returns an array of messages related to modifying cohort settings. If wait_for_messages
        is True, will wait for a message to appear.
        """
        title_css = "div.cohort-management-settings .message-" + type + " .message-title"
        detail_css = "div.cohort-management-settings .message-" + type + " .summary-item"

        return self._get_messages(title_css, detail_css, wait_for_messages=wait_for_messages)

    def _get_cohort_messages(self, type):
        """
        Returns array of messages related to manipulating cohorts directly through the UI for the given type.
        """
        title_css = "div.cohort-management-group-add .cohort-" + type + " .message-title"
        detail_css = "div.cohort-management-group-add .cohort-" + type + " .summary-item"

        return self._get_messages(title_css, detail_css)

    def get_csv_messages(self):
        """
        Returns array of messages related to a CSV upload of cohort assignments.
        """
        title_css = ".csv-upload .message-title"
        detail_css = ".csv-upload .summary-item"
        return self._get_messages(title_css, detail_css)

    def _get_messages(self, title_css, details_css, wait_for_messages=False):
        """
        Helper method to get messages given title and details CSS.
        """
        if wait_for_messages:
            EmptyPromise(
                lambda: self.q(css=self._bounded_selector(title_css)).results != 0,
                "Waiting for messages to appear"
            ).fulfill()
        message_title = self.q(css=self._bounded_selector(title_css))
        if len(message_title.results) == 0:
            return []
        messages = [message_title.first.text[0]]
        details = self.q(css=self._bounded_selector(details_css)).results
        for detail in details:
            messages.append(detail.text)
        return messages

    def get_cohort_confirmation_messages(self):
        """
        Returns an array of messages present in the confirmation area of the cohort management UI.
        The first entry in the array is the title. Any further entries are the details.
        """
        return self._get_cohort_messages("confirmations")

    def get_cohort_error_messages(self):
        """
        Returns an array of messages present in the error area of the cohort management UI.
        The first entry in the array is the title. Any further entries are the details.
        """
        return self._get_cohort_messages("errors")

    def get_cohort_related_content_group_message(self):
        """
        Gets the error message shown next to the content group selector for the currently selected cohort.
        If no message, returns None.
        """
        message = self.q(css=self._bounded_selector(".input-group-other .copy-error"))
        if not message:
            return None
        return message.results[0].text

    def select_data_download(self):
        """
        Click on the link to the Data Download Page.
        """
        self.q(css=self._bounded_selector("a.link-cross-reference[data-section=data_download]")).first.click()

    def upload_cohort_file(self, filename):
        """
        Uploads a file with cohort assignment information.
        """
        # If the CSV upload section has not yet been toggled on, click on the toggle link.
        cvs_upload_toggle = self.q(css=self._bounded_selector(".toggle-cohort-management-secondary")).first
        if cvs_upload_toggle:
            cvs_upload_toggle.click()
        path = InstructorDashboardPage.get_asset_path(filename)
        file_input = self.q(css=self._bounded_selector(self.csv_browse_button_selector_css)).results[0]
        file_input.send_keys(path)
        self.q(css=self._bounded_selector(self.csv_upload_button_selector_css)).first.click()


class MembershipPageAutoEnrollSection(PageObject):
    """
    CSV Auto Enroll section of the Membership tab of the Instructor dashboard.
    """
    url = None

    auto_enroll_browse_button_selector = '.auto_enroll_csv .file-browse input.file_field#browseBtn'
    auto_enroll_upload_button_selector = '.auto_enroll_csv button[name="enrollment_signup_button"]'
    NOTIFICATION_ERROR = 'error'
    NOTIFICATION_WARNING = 'warning'
    NOTIFICATION_SUCCESS = 'confirmation'

    def is_browser_on_page(self):
        return self.q(css=self.auto_enroll_browse_button_selector).present

    def is_file_attachment_browse_button_visible(self):
        """
        Returns True if the Auto-Enroll Browse button is present.
        """
        return self.q(css=self.auto_enroll_browse_button_selector).is_present()

    def is_upload_button_visible(self):
        """
        Returns True if the Auto-Enroll Upload button is present.
        """
        return self.q(css=self.auto_enroll_upload_button_selector).is_present()

    def click_upload_file_button(self):
        """
        Clicks the Auto-Enroll Upload Button.
        """
        self.q(css=self.auto_enroll_upload_button_selector).click()

    def is_notification_displayed(self, section_type):
        """
        Valid inputs for section_type: MembershipPageAutoEnrollSection.NOTIFICATION_SUCCESS /
                                       MembershipPageAutoEnrollSection.NOTIFICATION_WARNING /
                                       MembershipPageAutoEnrollSection.NOTIFICATION_ERROR
        Returns True if a {section_type} notification is displayed.
        """
        notification_selector = '.auto_enroll_csv .results .message-%s' % section_type
        self.wait_for_element_presence(notification_selector, "%s Notification" % section_type.title())
        return self.q(css=notification_selector).is_present()

    def first_notification_message(self, section_type):
        """
        Valid inputs for section_type: MembershipPageAutoEnrollSection.NOTIFICATION_WARNING /
                                       MembershipPageAutoEnrollSection.NOTIFICATION_ERROR
        Returns the first message from the list of messages in the {section_type} section.
        """
        error_message_selector = '.auto_enroll_csv .results .message-%s li.summary-item' % section_type
        self.wait_for_element_presence(error_message_selector, "%s message" % section_type.title())
        return self.q(css=error_message_selector).text[0]

    def upload_correct_csv_file(self):
        """
        Selects the correct file and clicks the upload button.
        """
        self._upload_file('auto_reg_enrollment.csv')

    def upload_csv_file_with_errors_warnings(self):
        """
        Selects the file which will generate errors and warnings and clicks the upload button.
        """
        self._upload_file('auto_reg_enrollment_errors_warnings.csv')

    def upload_non_csv_file(self):
        """
        Selects an image file and clicks the upload button.
        """
        self._upload_file('image.jpg')

    def _upload_file(self, filename):
        """
        Helper method to upload a file with registration and enrollment information.
        """
        file_path = InstructorDashboardPage.get_asset_path(filename)
        self.q(css=self.auto_enroll_browse_button_selector).results[0].send_keys(file_path)
        self.click_upload_file_button()


class DataDownloadPage(PageObject):
    """
    Data Download section of the Instructor dashboard.
    """
    url = None

    def is_browser_on_page(self):
        return self.q(css='a[data-section=data_download].active-section').present

    def get_available_reports_for_download(self):
        """
        Returns a list of all the available reports for download.
        """
        reports = self.q(css="#report-downloads-table .file-download-link>a").map(lambda el: el.text)
        return reports.results
