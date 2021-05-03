from django.contrib.auth import authenticate
from django.http.response import HttpResponse
from django.shortcuts import render
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
from wsgiref.util import FileWrapper

from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import CreateAPIView, RetrieveAPIView, GenericAPIView,  UpdateAPIView
from rest_framework import mixins, status

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.response import Response
from rest_framework.views import APIView

from base_app.error_codes import ApplicationErrorException
from common.util.http_helpers import ok, bad_request, no_content
from panelprofile.models import AuthDoc
from panelprofile.permissions import AuthDocsNotUploaded, IsPhoneNotVerified
from panelprofile.serializers import AuthSerializer, BusinessmanProfileSerializer, UploadImageSerializer,\
    SMSPanelInfoSerializer
from panelprofile.services import sms_panel_info_service
from users.models import Businessman

from common.util.custom_permission import HasUploadedAuthDocsAndAuthenticated
from users.services import verification_service, businessman_service


class BusinessmanRetrieveUpdateProfileAPIView(APIView):

    """
    put:
    Updates the profile of the user. Needs JWT token

    get:
    Retrieves the profile data Including phone, business_name, first_name, last_name, email.
     but phone number and business name are required. Needs JWT toeken
    """

    def put(self, request, *args, **kwargs):
        serializer = BusinessmanProfileSerializer(data=request.data, context={'user': request.user, 'request': request})

        if not serializer.is_valid():
            return bad_request(serializer.errors)

        businessman_service.update_businessman_profile(
            request.user,
            serializer.validated_data.get('first_name'),
            serializer.validated_data.get('last_name'),
            serializer.validated_data.get('business_name'),
            serializer.validated_data.get('category'),
            serializer.validated_data.get('phone'),
            serializer.validated_data.get('email')
        )

        serializer = BusinessmanProfileSerializer(request.user, request=request)

        return ok(serializer.data)

    def get(self, request, *args, **kwargs):
        serializer = BusinessmanProfileSerializer(request.user, context={'user': request.user, 'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)


class UploadRetrieveProfileImage(APIView):

    def put(self, request: Request):

        """
        NEW
        content-type : multipart/form-data
        field in body:
        logo : image file that must be uploaded. size limit: 200 kb

        Receives and saves sent logo image for logged in user.
        :param request: Contain data of Http request
        :return: If sends data is npt valid Response object with 400 status code else, Response Object with 200 status code

        """

        serializer = UploadImageSerializer(data=request.data)

        serializer._context = {'user': request.user}

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.update(request.user, serializer.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)

    # def get(self, request: Request):
    #
    #     """
    #     NEW
    #     Gives the logo image that is uploaded by put request
    #     :param request:
    #     :return: If an logo file is uploaded before returns Response with file and 200 status code, else 404 status code
    #     """
    #
    #     logo = request.user.logo
    #     if not logo:
    #         return Response(status=status.HTTP_404_NOT_FOUND)
    #
    #     return HttpResponse(FileWrapper(logo.file), content_type="image/png")


class SendPhoneVerificationCode(APIView):

    permission_classes = [IsPhoneNotVerified]

    def post(self, request: Request):
        try:
            vcode = verification_service.create_send_phone_confirm_verification_code(request.user)
            data = {'verification_code_id': vcode.id}
            return ok(data)
        except ApplicationErrorException as e:
            return bad_request(e.http_message)


class ResendVerificationCode(APIView):

    permission_classes = [IsPhoneNotVerified]

    def post(self, request: Request, verification_code_id: int):

        try:
            verification_service.resend_phone_confirm_code(request.user, verification_code_id)
        except ApplicationErrorException as e:
            return bad_request(e.http_message)
        return no_content()

class VerifyPhone(APIView):

    permission_classes = [IsPhoneNotVerified]

    def post(self, request: Request, verification_code_id: int, code: str):

        try:
            verification_service.check_phone_confirm_code_is_valid_and_delete(request.user, verification_code_id, code)
        except ApplicationErrorException as e:
            return bad_request(e.http_message)
        serializer = BusinessmanProfileSerializer(request.user, context={'user': request.user, 'request': request})
        return ok(serializer.data)


@api_view(['GET'])
@permission_classes([])
def get_user_logo(request: Request, businessman_id):

    """
    NEW
    Gives the logo image that is uploaded by put request
    :param request:
    :param businessman_id: id of the user that logo belongs to
    :return: If an logo file is uploaded before returns Response with file and 200 status code, else 404 status code
    """

    try:
        user = Businessman.objects.get(id=businessman_id)
    except ObjectDoesNotExist:
        return Response({'details': 'کاربری یافت نشد'},status=status.HTTP_404_NOT_FOUND)

    logo = user.logo
    if not logo:
        return Response({'details': 'این کاربر لوگو خود را ثبت نکرده'}, status=status.HTTP_404_NOT_FOUND)

    return HttpResponse(FileWrapper(logo.file), content_type="image/png")




class UploadBusinessmanDocs(CreateAPIView):

    """
    handles upload of authorization documents that is needed to authorize user
    """

    serializer_class = AuthSerializer
    permission_classes = [permissions.IsAuthenticated, AuthDocsNotUploaded]

    def get_serializer_context(self):
        return {'user': self.request.user}
