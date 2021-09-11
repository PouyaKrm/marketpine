from django.http.response import HttpResponse
from django.core.exceptions import ObjectDoesNotExist

# Create your views here.
from wsgiref.util import FileWrapper

from rest_framework.decorators import api_view, permission_classes
from rest_framework import status

from rest_framework import permissions
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from common.util.http_helpers import ok, bad_request, no_content, created
from panelprofile.permissions import AuthDocsNotUploaded, IsPhoneNotVerified
from panelprofile.serializers import AuthSerializer, BusinessmanProfileSerializer, UploadImageSerializer, \
    PhoneChangeSerializer
from panelprofile.services import business_man_auth_doc_service
from users.models import Businessman

from users.permissions import IsPhoneVerified, IsProfileComplete
from users.services import verification_service, businessman_service
# Create your views here.
from wsgiref.util import FileWrapper

from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponse
from rest_framework import permissions
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from common.util.http_helpers import ok, bad_request, no_content, created
from panelprofile.permissions import AuthDocsNotUploaded, IsPhoneNotVerified
from panelprofile.serializers import AuthSerializer, BusinessmanProfileSerializer, UploadImageSerializer, \
    PhoneChangeSerializer
from panelprofile.services import business_man_auth_doc_service
from users.models import Businessman
from users.permissions import IsPhoneVerified, IsProfileComplete
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
            serializer.validated_data.get('email'),
            serializer.validated_data.get('viewed_intro')
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

        serializer = UploadImageSerializer(data=request.data, request=request)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.update(request.user, serializer.validated_data)

        serializer = UploadImageSerializer(user, request=request)

        return ok(serializer.data)


class SendPhoneVerificationCode(APIView):
    permission_classes = [permissions.IsAuthenticated, IsPhoneNotVerified]

    def post(self, request: Request):

        resend = request.query_params.get('resend')

        if resend is not None and resend.lower().strip() == 'true':
            verification_service.resend_phone_confirm_code(request.user)
            return no_content()

        sr = PhoneChangeSerializer(data=request.data, request=request)

        if not sr.is_valid():
            return bad_request(sr.errors)

        businessman_service.send_businessman_phone_verification(request.user, sr.validated_data.get('phone'))
        return no_content()


class VerifyPhone(APIView):
    permission_classes = [permissions.IsAuthenticated, IsPhoneNotVerified]

    def post(self, request: Request, code: str):
        businessman_service.verify_businessman_phone(request.user, code)
        serializer = BusinessmanProfileSerializer(request.user, context={'user': request.user, 'request': request})
        return ok(serializer.data)


class PhoneChangeSendVerification(APIView):
    permission_classes = [permissions.IsAuthenticated, IsPhoneVerified]

    def post(self, request: Request):

        resend = request.query_params.get('resend')

        if resend is not None and resend.lower().strip() == 'true':
            verification_service.resend_phone_change_code(request.user)
            return no_content()

        sr = PhoneChangeSerializer(is_phone_required=True, data=request.data, request=request)
        if not sr.is_valid():
            return bad_request(sr.errors)

        businessman_service.send_phone_change_verification(request.user, sr.validated_data.get('phone'))
        return no_content()


class PhoneChangeVerify(APIView):
    permission_classes = [permissions.IsAuthenticated, IsPhoneVerified]

    def post(self, request: Request, previous_phone_code: str, new_phone_code: str):
        user = businessman_service.change_phone_number(request.user, previous_phone_code, new_phone_code)
        sr = BusinessmanProfileSerializer(user, request=request)
        return ok(sr.data)


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
        return Response({'details': 'کاربری یافت نشد'}, status=status.HTTP_404_NOT_FOUND)

    logo = user.logo
    if not logo:
        return Response({'details': 'این کاربر لوگو خود را ثبت نکرده'}, status=status.HTTP_404_NOT_FOUND)

    return HttpResponse(FileWrapper(logo.file), content_type="image/png")


class UploadBusinessmanDocs(APIView):
    """
    handles upload of authorization documents that is needed to authorize user
    """

    permission_classes = [permissions.IsAuthenticated, IsPhoneVerified, IsProfileComplete, AuthDocsNotUploaded]

    def post(self, request):
        sr = AuthSerializer(data=request.data, request=request)
        if not sr.is_valid():
            return bad_request(sr.errors)

        doc = business_man_auth_doc_service.businessman_auth_docs_upload(
            request.user,
            sr.validated_data.get('form'),
            sr.validated_data.get('national_card'),
            sr.validated_data.get('birth_certificate'),
            sr.validated_data.get('password')
        )
        return created()
