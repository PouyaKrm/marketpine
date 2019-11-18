from django.contrib.auth import authenticate
from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.
from wsgiref.util import FileWrapper

from rest_framework.generics import CreateAPIView, RetrieveAPIView, GenericAPIView,  UpdateAPIView
from rest_framework import mixins, status

from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from panelprofile.models import AuthDoc
from panelprofile.permissions import AuthDocsNotUploaded
from panelprofile.serializers import AuthSerializer, BusinessmanProfileSerializer
from users.models import Businessman


class BusinessmanRetrieveUpdateProfileAPIView(APIView):

    """
    put:
    Updates the profile of the user. Needs JWT token

    get:
    Retrieves the profile data Including phone, business_name, first_name, last_name, email.
     but phone number and business name are required. Needs JWT toeken
    """

    def put(self, request, *args, **kwargs):
        serializer = BusinessmanProfileSerializer(data=request.data)

        serializer._context = {'user': self.request.user}

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = Businessman.objects.get(id=self.request.user.id)

        serializer.update(user, serializer.validated_data)

        serializer.instance = user

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):
        serializer = BusinessmanProfileSerializer(self.request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)


class UploadBusinessmanDocs(CreateAPIView):

    """
    handles upload of authorization documents that is needed to authorize user
    """

    serializer_class = AuthSerializer
    permission_classes = [permissions.IsAuthenticated, AuthDocsNotUploaded]

    def get_serializer_context(self):
        return {'user': self.request.user}


# TODO move file download to separate app and add Nginx config to Nginx serve the files
def get_auth_pdf_doc(request):

    if AuthDoc.objects.exists():
        qs = AuthDoc.objects.all()[0]
    else:
        qs = None

    if qs is not None:
        return HttpResponse(FileWrapper(qs.file), content_type='application/pdf')
    return HttpResponse(status=404)

