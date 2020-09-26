from rest_framework import serializers

from base_app.serializers import FileFieldWithLinkRepresentation
from educations.models import EducationType, Education


class EducationTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = EducationType
        fields = [
            'id',
            'name'
        ]


class EducationSerializer(serializers.ModelSerializer):
    education_type = EducationTypeSerializer(read_only=True)
    video = FileFieldWithLinkRepresentation

    class Meta:
        model = Education
        fields = '__all__'
