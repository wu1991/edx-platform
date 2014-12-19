from django.core.urlresolvers import reverse
from django.test import TestCase
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory


def serialize_course(course):
    return {
        'id': unicode(course.id),
        'name': course.display_name
    }


INVALID_COURSE_ID = 'foo/bar/baz'
COURSE_NAME = 'An Introduction to API Testing'
COURSE = CourseFactory.create(display_name=COURSE_NAME)
COURSE_ID = unicode(COURSE.id)
COURSE_SERIALIZED = serialize_course(COURSE)

ASSIGNMENT = ItemFactory.create(
    category="sequential",
    parent_location=COURSE.location,
    display_name="Lesson 1",
    format="Homework",
    graded=True
)

PROBLEM = ItemFactory.create(
    category="problem",
    parent_location=ASSIGNMENT.location,
    display_name="Problem 1"
)


class CourseListTests(TestCase):
    def test_get(self):
        """
        The view should return a list of details for all courses.
        """
        response = self.client.get(reverse('course_api:v0:list'))
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(response.data, [COURSE_SERIALIZED])

    def test_get_filtering(self):
        """
        The view should return a list of details for the specified courses.
        """
        self.fail()


class CourseDetailTests(TestCase):
    def test_get(self):
        """
        The view should return details for a course.
        """
        response = self.client.get(reverse('course_api:v0:detail', kwargs={'course_id': COURSE_ID}))
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(response.data, COURSE_SERIALIZED)

    def test_get_invalid_course(self):
        """
        The view should return a 404 if the course ID is invalid.
        """
        response = self.client.get(reverse('course_api:v0:detail', kwargs={'course_id': INVALID_COURSE_ID}))
        self.assertEqual(response.status_code, 404)


class CourseAssignmentsTests(TestCase):
    def test_get(self):
        """
        The view should return assignments for a course.
        """
        response = self.client.get(reverse('course_api:v0:assignments', kwargs={'course_id': COURSE_ID}))
        self.assertEqual(response.status_code, 200)

        expected = [
            {
                'id': unicode(ASSIGNMENT.location),
                'name': ASSIGNMENT.display_name,
                'assignment_type': 'Homework',
                'problems': [
                    {
                        'id': unicode(PROBLEM.location),
                        'name': PROBLEM.display_name
                    }
                ]
            }
        ]
        self.assertListEqual(response.data, expected)

    def test_get_invalid_course(self):
        """
        The view should return a 404 if the course ID is invalid.
        """
        response = self.client.get(reverse('course_api:v0:assignments', kwargs={'course_id': INVALID_COURSE_ID}))
        self.assertEqual(response.status_code, 404)
