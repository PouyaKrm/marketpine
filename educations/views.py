from django.shortcuts import render

# Create your views here.
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination

from common.util.http_helpers import ok
from educations.models import Education
from educations.serializers import EducationSerializer, EducationTypeSerializer
from educations.services import education_service


class EducationListPaginator(PageNumberPagination):
    page_size = 6


class EducationsListAPIView(ListAPIView):

    serializer_class = EducationSerializer
    pagination_class = EducationListPaginator

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


@api_view(['GET'])
def get_education_type_list(request):
    types = education_service.get_all_education_types()
    sr = EducationTypeSerializer(types, many=True)
    return ok(sr.data)
