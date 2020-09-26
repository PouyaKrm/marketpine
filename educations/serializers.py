from rest_framework import serializers

from base_app.serializers import FileFieldWithLinkRepresentation
from educations.models import EducationType, Education


class EducationSerializer(serializers.ModelSerializer):
    class EducationTypeSerializer(serializers.ModelSerializer):
        class Meta:
            model = EducationType
            fields = [
                'id',
                'name'
            ]

    education_type = EducationTypeSerializer(read_only=True)
    video = FileFieldWithLinkRepresentation

    class Meta:
        model = Education
        fields = '__all__'
