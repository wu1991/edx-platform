from rest_framework import serializers


class BaseSerializer(serializers.Serializer):
    id = serializers.CharField(source='location')
    name = serializers.CharField(source='display_name')


class CourseSerializer(BaseSerializer):
    id = serializers.CharField(source='id')


class ProblemSerializer(BaseSerializer):
    pass


class AssignmentSerializer(BaseSerializer):
    assignment_type = serializers.CharField(source='format')
    problems = ProblemSerializer(many=True)
