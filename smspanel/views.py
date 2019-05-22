import coreapi
import coreschema
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from rest_framework import generics, mixins, permissions, status, schemas
from rest_framework.decorators import api_view, schema, permission_classes
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema

from .serializers import SMSTemplateSerializer, SentSMSSerializer
from .models import SMSTemplate, SentSMS


# Create your views here.


class SMSTemplateCreateListAPIView(generics.ListAPIView, mixins.CreateModelMixin):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SMSTemplateSerializer

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_queryset(self):
        return SMSTemplate.objects.filter(businessman=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SMSTemplateRetrieveAPIView(generics.RetrieveAPIView, mixins.UpdateModelMixin,
                                 mixins.DestroyModelMixin):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SMSTemplateSerializer

    def get_queryset(self):
        return SMSTemplate.objects.filter(businessman=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_plain_sms(request):

    serializer = SentSMSSerializer(data=request.data)

    serializer._context = {'user': request.user, 'is_plain': True}

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.create(serializer.validated_data)

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_sms_by_template(request, template_id):

    try:
        template = SMSTemplate.objects.get(businessman=request.user, id=template_id)

    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    request.data['content'] = template.content
    # obj = SentSMS(data=)


    serializer = SentSMSSerializer(data=request.data)

    serializer._context = {'user': request.user, 'is_plain': False}

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.create(serializer.validated_data)

    return Response(status=status.HTTP_204_NO_CONTENT)






