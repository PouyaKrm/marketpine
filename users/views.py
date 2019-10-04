import jwt
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.request import Request
from django.contrib.auth import authenticate

from common.util import  get_client_ip, custom_login_payload
from users.models import BusinessmanRefreshTokens
from .serializers import *
# Create your views here.
from rest_framework import generics
import os
from django.conf import settings
from django.http.response import HttpResponse
from wsgiref.util import FileWrapper
from .permissions import HasValidRefreshToken


class RegisterSalesmanView(generics.CreateAPIView):

    permission_classes = []
    authentication_classes = []
    serializer_class = BusinessmanRegisterSerializer
    queryset = Businessman.objects.all()


@api_view(['POST'])
@permission_classes([])
def create_user(request):

    """
    Registers new users or salesman. It Needs to be activated by the admin to be able to login
    """

    serializer = BusinessmanRegisterSerializer(data=request.data)

    if not serializer.is_valid():

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()

    return Response(data={'id': user.id}, status=status.HTTP_201_CREATED)



@api_view(['GET'])
@permission_classes([])
def resend_verification_code(request, user_id):

    try:

        user = Businessman.objects.get(id=user_id)

        verify_code = user.verificationcodes

    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if verify_code.num_requested == 3:

        return Response(status=status.HTTP_403_FORBIDDEN)

    verify_code.num_requested += 1

    verify_code.save()

    # code = verify_code.code

    SMSMessage().send_verification_code(user.phone, verify_code.code)

    return Response(status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([])
def login_api_view(request):

    """
    Creates a refresh token for a user.
    :param request:
    :return: If request data is invalid sends HTTP Response with 400 status code. Else if user does not exist or is not
    verified returns Response with error message and 401 status code. Else Response with token and additional data and
    200 status code.
    """

    serializer = BusinessmanLoginSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=request.data.get('username'), password=request.data.get('password'))

    if user is None or user.is_verified is False:
        return Response({'details': ['username or password is wrong']}, status=status.HTTP_401_UNAUTHORIZED)

    expire_time = datetime.datetime.now() + settings.REFRESH_TOKEN_EXP_DELTA

    obj = BusinessmanRefreshTokens.objects.create(username=user.get_username(), expire_at=expire_time,
                                            ip=get_client_ip(request))

    payload = {'exp': expire_time, "iss": user.get_username(), "iat": datetime.datetime.now(), 'id': obj.id}

    token = jwt.encode(payload, settings.REFRESH_KEY_PR, algorithm='RS256')

    response = {'refresh_token': token}
    response['exp'] = expire_time
    response['id'] = user.id
    response['username'] = user.get_username()
    response['business_name'] = user.business_name
    response['exp_duration'] = settings.REFRESH_TOKEN_EXP_DELTA


    return Response(response, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([HasValidRefreshToken])
def get_access_token(request):

    """
    NEW
    Generates access token for the user that has refresh token. Every time an access token is needed like when token is
    expired, Should make request to this endpoint
    headers: x-api-key header that contains refresh token is needed
    :param request:
    :return:
    """

    username = request.data['username']

    try:
        user = Businessman.objects.get(username=username, is_verified=True)
    except ObjectDoesNotExist:
        return Response({'details': ['provided data is invalid']}, status=status.HTTP_401_UNAUTHORIZED)
    payload = custom_login_payload(user)

    return Response(payload, status=status.HTTP_200_OK)



@api_view(['PUT'])
@permission_classes([])
def verify_user(request, code):

    try:
        verify_code = VerificationCodes.objects.get(code=code)

    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    verify_code.businessman.is_verified = True

    verify_code.businessman.save()

    verify_code.delete()

    return Response(status=status.HTTP_204_NO_CONTENT)





@api_view(['PUT'])
def reset_user_password(request):

    """
    Resets the password of the user. Needs JWT token
    """

    serializer = BusinessmanPasswordResetSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=request.user.username, password=request.data.get('old_password'))
    if user is None:
        return Response(status=status.HTTP_403_FORBIDDEN)

    serializer.update(request.user, serializer.validated_data)

    return Response(status=status.HTTP_204_NO_CONTENT)






@api_view(['PUT'])
@permission_classes([])
def user_forget_password(request):

    serializer = BusinessmanForgetPasswordSerializer(data=request.data)

    if not serializer.is_valid():

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:

        user = Businessman.objects.get(username=request.data['username'], phone=request.data['phone'])

    except ObjectDoesNotExist:

        return Response(status=status.HTTP_404_NOT_FOUND)



    serializer.update(user, serializer.validated_data)

    return Response(status=status.HTTP_204_NO_CONTENT)





class SalesmanRetrieveUpdateAPIView(APIView):

    """
    put:
    Updates the profile of the user. Needs JWT token

    get:
    Retrieves the profile data Including phone, business_name, first_name, last_name, email.
     but phone number and business name are required. Needs JWT toeken
    """

    def put(self, request, *args, **kwargs):

        serializer = BusinessmanRetrieveSerializer(data=request.data)

        serializer._context = {'request': self.request}

        if not serializer.is_valid():

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = Businessman.objects.get(id=self.request.user.id)

        serializer.update(user, serializer.validated_data)

        serializer.instance = user

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):

        serializer = BusinessmanRetrieveSerializer(self.request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)





class image_up(generics.CreateAPIView):

    def get_queryset(self):
        return self.request.user.logo

    serializer_class = UploadImageSerializer


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
