from django.contrib.auth import authenticate
from django.http.response import HttpResponse
from django.shortcuts import render

# Create your views here.
from wsgiref.util import FileWrapper
from common.util.kavenegar_local import APIException
from rest_framework import status, permissions
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser

from panelprofile.models import AuthDoc, BusinessmanAuthDocs
from panelprofile.permissions import IsUnAuthorized, IsAuthDocsUploaded
from panelprofile.serializers import AuthAuthenticateUserSerializer, AuthFormSerializer, AuthNationalCardSerializer, \
    AuthBirthCertificateSerializer

def create_businessman_auth_docs(user):
    if not hasattr(user, 'businessmanauthdocs'):
        return BusinessmanAuthDocs.objects.create(businessman=user)


@api_view(['POST'])
@parser_classes([MultiPartParser])
@permission_classes([permissions.IsAuthenticated, IsUnAuthorized])
def upload_auth_docs(request: Request, doc_type):

    """
    updates auth docs that needed to authorize user.
    docs are taken based on the path variable 'doc_type':
        form: to upload form document.
        card: to upload national card image.
        certificate: to upload birth certificate
    :parameter doc_type specifies witch file must be validated abd stored
    :param request:
    :return: if param is not sent or file with key 'file' does not exist,
    Returns Response with error message and 400 status code. else Response with 204 if operation was successful
    """
    if not request.data.keys().__contains__('file'):
        return Response({'details': 'no file is sent'}, status=status.HTTP_400_BAD_REQUEST)

    if doc_type == 'form':
        serializer = AuthFormSerializer(data={'form': request.data['file']})
    elif doc_type == 'card':
        serializer = AuthNationalCardSerializer(data={'national_card': request.data['file']})
    elif doc_type == 'certificate':
        serializer = AuthBirthCertificateSerializer(data={'birth_certificate': request.data['file']})
    else:
        return Response({'param': 'doc_type must be form, card or certificate'}, status=status.HTTP_400_BAD_REQUEST)

    create_businessman_auth_docs(request.user)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.update(request.user.businessmanauthdocs, serializer.validated_data)

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, IsUnAuthorized, IsAuthDocsUploaded])
def authenticate_user(request: Request):

    """
    authenticate user by password is sent. and finishes authentication
    :param request:
    :return: If data is invalid Response with status code 400, else if password was incorrect Response with 401 status code
    else Response 204 if operation was successful. if an error occurs on kavenegar api. it will forward the error
    to the client
    """

    serializer = AuthAuthenticateUserSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

    serializer.businessman(request.user)

    user = authenticate(username=request.user.username, password = serializer.validated_data['password'])

    if user is None:
        return Response({'detail': 'username or password is wrong'}, status=status.HTTP_401_UNAUTHORIZED)

    try:
        serializer.create(serializer.validated_data)
    except APIException as e:
        return Response({'detail': e.message}, status=e.status)

    return Response(status=status.HTTP_204_NO_CONTENT)


# TODO move file download to separate app and add Nginx config to Nginx serve the files
def get_auth_pdf_doc(request):

    if AuthDoc.objects.exists():
        qs = AuthDoc.objects.all()[0]
    else:
        qs = None

    if qs is not None:
        return HttpResponse(FileWrapper(qs.file), content_type='application/pdf')
    return HttpResponse(status=404)

