from django.http import Http404
from rest_framework import generics
from xmodule.modulestore.django import modulestore
from opaque_keys.edx.keys import CourseKey
from course_api.v0.serializers import CourseSerializer, AssignmentSerializer


class CourseList(generics.ListAPIView):
    serializer_class = CourseSerializer

    def get_queryset(self):
        """
        Retrieve the courses from the module store.
        """
        return modulestore().get_courses()


class CourseDetail(generics.RetrieveAPIView):
    serializer_class = CourseSerializer
    lookup_field = 'course_id'

    def get_object(self):
        """
        Retrieve the course from the module store.
        """
        course_id = self.kwargs.get('course_id')
        course_key = CourseKey.from_string(course_id)
        course = modulestore().get_course(course_key)

        if not course:
            raise Http404
        return course


class CourseAssignments(generics.ListAPIView):
    serializer_class = AssignmentSerializer
    allow_empty = False

    def _filter_problems(self, node):
        if node.category == u'problem':
            return [node]

        if not node.has_children:
            return []

        problems = []
        for child in node.get_children():
            problems += self._filter_problems(child)

        return problems

    def get_course_assignments(self, course_key):
        """
        Retrieve course assignments (e.g. homework, exams) from the module store.
        """
        ms = modulestore()

        # Ensure the course exists
        if not ms.get_course(course_key):
            raise Http404

        assignments = ms.get_items(course_key, settings={'graded': True})

        for assignment in assignments:
            problems = self._filter_problems(assignment)
            assignment.problems = problems

        return assignments

    def get_queryset(self):
        course_id = self.kwargs.get('course_id')
        course_key = CourseKey.from_string(course_id)
        return self.get_course_assignments(course_key)
