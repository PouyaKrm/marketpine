from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView

from educations.models import Education
from educations.serializers import EducationSerializer
from educations.services import education_service


class EducationsListAPIView(ListAPIView):

    serializer_class = EducationSerializer

    def get_queryset(self):
        type_id = self.request.query_params.get('type')
        if type_id is None:
            return education_service.get_all_educations()
        try:
            type_id = int(type_id)
            return education_service.get_all_educations(type_id)
        except ValueError:
            return education_service.get_all_educations()

    def get_serializer_context(self):
        return {'request': self.request}
