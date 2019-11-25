from django.shortcuts import render

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework import permissions
from rest_framework import status

from common.util.custom_permission import HasUploadedAuthDocsAndAuthenticated

from download import attach_file
# Create your views here.


@api_view(['GET'])
def download_logo(request: Request):

    """
    gives the path of the logo file to be served by nginx
    """

    logo = request.user.logo

    return attach_file(logo)

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, HasUploadedAuthDocsAndAuthenticated])
def download_auth_docs(request: Request, file_type: str):

    if file_type=='form':
        file = request.user.businessmanauthdocs.form
    elif file_type=='card':
        file = request.user.businessmanauthdocs.national_card
    elif file_type=='certificate':
        file = request.user.businessmanauthdocs.birth_certificate
    else:
        return Response(status=status.HTTP_404_NOT_FOUND)

    return attach_file(file)



