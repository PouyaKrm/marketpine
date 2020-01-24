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

    SystemSMSMessage().send_verification_code(user.phone, verify_code.code)

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
