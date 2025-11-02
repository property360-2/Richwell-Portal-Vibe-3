from rest_framework import serializers
from .models import Subject, SubjectPrerequisite

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = "__all__"

class SubjectPrerequisiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubjectPrerequisite
        fields = "__all__"
