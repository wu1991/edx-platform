"""
End-to-end test for cohorted courseware. This uses both Studio and LMS.
"""

from nose.plugins.attrib import attr
import json

from studio.base_studio_test import ContainerBase

from ..pages.studio.settings_group_configurations import GroupConfigurationsPage
from ..pages.studio.settings_advanced import AdvancedSettingsPage
from ..pages.studio.auto_auth import AutoAuthPage
from ..fixtures.course import XBlockFixtureDesc
from ..pages.studio.component_editor import ComponentVisibilityEditorView
from ..pages.lms.instructor_dashboard import InstructorDashboardPage
from ..pages.lms.course_nav import CourseNavPage
from ..pages.lms.courseware import CoursewarePage

from bok_choy.promise import EmptyPromise


@attr('shard_1')
class EndToEndCohortedCoursewareTest(ContainerBase):

    def setUp(self, is_staff=True):

        super(EndToEndCohortedCoursewareTest, self).setUp(is_staff=is_staff)
        self.staff_user = self.user

        self.content_group_a = "Content Group A"
        self.content_group_b = "Content Group B"

        # Create a student who will be in "Cohort A"
        self.cohort_a_student_username = "cohort_a_student"
        self.cohort_a_student_email="cohort_a_student@example.com"
        AutoAuthPage(
            self.browser, username=self.cohort_a_student_username, email=self.cohort_a_student_email, no_login=True
        ).visit()

        # Create a student who will be in "Cohort B"
        self.cohort_b_student_username = "cohort_b_student"
        self.cohort_b_student_email="cohort_b_student@example.com"
        AutoAuthPage(
            self.browser, username=self.cohort_b_student_username, email=self.cohort_b_student_email, no_login=True
        ).visit()

        # Create a student who will end up in the Default cohort group
        self.cohort_default_student_username = "cohort default student"
        self.cohort_default_student_email ="cohort_default_student@example.com"
        AutoAuthPage(
            self.browser, username=self.cohort_default_student_username,
            email=self.cohort_default_student_email, no_login=True
        ).visit()

        # Start logged in as the staff user.
        AutoAuthPage(
            self.browser, username=self.staff_user["username"], email=self.staff_user["email"]
        ).visit()

    def populate_course_fixture(self, course_fixture):
        """
        Populate the children of the test course fixture.
        """
        self.group_a_problem = 'Group A Content'
        self.group_b_problem = 'Group B Content'
        self.group_a_and_b_problem = 'Group A and B Content'
        self.visible_to_all_problem = 'Visible to All Content'
        course_fixture.add_children(
            XBlockFixtureDesc('chapter', 'Test Section').add_children(
                XBlockFixtureDesc('sequential', 'Test Subsection').add_children(
                    XBlockFixtureDesc('vertical', 'Test Unit').add_children(
                        XBlockFixtureDesc('problem', self.group_a_problem, data='<problem></problem>'),
                        XBlockFixtureDesc('problem', self.group_b_problem, data='<problem></problem>'),
                        XBlockFixtureDesc('problem', self.group_a_and_b_problem, data='<problem></problem>'),
                        XBlockFixtureDesc('problem', self.visible_to_all_problem, data='<problem></problem>'),
                    )
                )
            )
        )

    def _enable_cohorts_in_course(self):
        """
        This turns on cohorts for the course. Currently this is still done through Advanced
        Settings. Eventually it will be done in the Instructor Dashboard.
        """
        advanced_settings = AdvancedSettingsPage(
            self.browser,
            self.course_info['org'],
            self.course_info['number'],
            self.course_info['run']
        )

        advanced_settings.visit()
        cohort_config = '{"cohorted": true}'
        advanced_settings.set('Cohort Configuration', cohort_config)
        advanced_settings.refresh_and_wait_for_load()

        self.assertEquals(
            json.loads(cohort_config),
            json.loads(advanced_settings.get('Cohort Configuration')),
            'Wrong input for Cohort Configuration'
        )

    def _create_content_groups(self):
        """
        Creates two content groups in Studio Group Configurations Settings.
        """
        group_configurations_page = GroupConfigurationsPage(
            self.browser,
            self.course_info['org'],
            self.course_info['number'],
            self.course_info['run']
        )
        group_configurations_page.visit()

        group_configurations_page.create_first_content_group()
        config = group_configurations_page.content_groups[0]
        config.name = self.content_group_a
        config.save()

        group_configurations_page.add_content_group()
        config = group_configurations_page.content_groups[1]
        config.name = self.content_group_b
        config.save()

    def _link_problems_to_content_groups_and_publish(self):
        """
        Updates 3 of the 4 existing problems to limit their visibility by content group.
        Publishes the modified unit.
        """
        container_page = self.go_to_unit_page()
        problem_a_only = container_page.xblocks[1]
        problem_b_only = container_page.xblocks[2]
        problem_a_and_b = container_page.xblocks[3]

        problem_a_only.edit_visibility()
        ComponentVisibilityEditorView(self.browser, problem_a_only.locator).select_option(self.content_group_a)

        problem_b_only.edit_visibility()
        ComponentVisibilityEditorView(self.browser, problem_b_only.locator).select_option(self.content_group_b)

        problem_a_and_b.edit_visibility()
        visibility_editor = ComponentVisibilityEditorView(self.browser, problem_a_and_b.locator)
        visibility_editor.select_option(self.content_group_a, save=False)
        visibility_editor.select_option(self.content_group_b)
        container_page.publish_action.click()

    def _create_cohorts_and_assign_students(self):
        """
        Adds 2 manual cohorts, linked to content groups, to the course.
        Each cohort is assigned one student.
        """
        instructor_dashboard_page = InstructorDashboardPage(self.browser, self.course_id)
        instructor_dashboard_page.visit()
        membership_page = instructor_dashboard_page.select_membership()
        cohort_management_page = membership_page.select_cohort_management_section()

        def add_cohort_with_student(cohort_name, content_group, student):
            cohort_management_page.add_cohort(cohort_name, content_group=content_group)
            # After adding the cohort, it should automatically be selected
            EmptyPromise(
                lambda: cohort_name == cohort_management_page.get_selected_cohort(), "Waiting for new cohort"
            ).fulfill()
            cohort_management_page.add_students_to_selected_cohort([student])

        add_cohort_with_student("Cohort A", self.content_group_a, self.cohort_a_student_username)
        add_cohort_with_student("Cohort B", self.content_group_b, self.cohort_b_student_username)

    def _view_cohorted_content_as_different_users(self):
        """
        View content as staff, student in Cohort A, student in Cohort B, and student in Default Cohort.
        """
        courseware_page = CoursewarePage(self.browser, self.course_id)
        courseware_page.visit()

        # We are already logged in as staff, so view that way first.
        def verify_visible_problems(expected_items):
            course_nav = CourseNavPage(self.browser)
            actual_items = course_nav.sequence_items
            self.assertItemsEqual(expected_items, actual_items)

        verify_visible_problems(
            [self.group_a_problem, self.group_b_problem, self.group_a_and_b_problem, self.visible_to_all_problem]
        )

    def test_cohorted_courseware(self):
        """

        """
        #self._enable_cohorts_in_course()
        #self._create_content_groups()
        #self._link_problems_to_content_groups_and_publish()
        #self._create_cohorts_and_assign_students()
        self._view_cohorted_content_as_different_users()