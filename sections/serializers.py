from rest_framework import serializers
from .models import Section, AssignedSubject
from users.models import User

class SectionSerializer(serializers.ModelSerializer):
    professors = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="PROFESSOR"), many=True, required=False
    )

    class Meta:
        model = Section
        fields = "__all__"


class AssignedSubjectSerializer(serializers.ModelSerializer):
    professors = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(role="PROFESSOR"), many=True, required=False
    )

    class Meta:
        model = AssignedSubject
        fields = "__all__"
