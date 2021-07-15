from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response

from base_app.error_codes import ApplicationErrorException
from common.util.http_helpers import ok, not_found, dependency_failed, no_content, bad_request
from .permissions import HasValidRefreshToken
from .serializers import *
from .services import businessman_service


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
        return bad_request(serializer.errors)

    try:
        user = businessman_service.register_user(
            serializer.validated_data.get('username'),
            serializer.validated_data.get('password'),
            serializer.validated_data.get('phone'),
            serializer.validated_data.get('email'),
            serializer.validated_data.get('first_name'),
            serializer.validated_data.get('last_name')
        )

        auth_result = businessman_service.login_user(user.username,
                                                     serializer.validated_data.get('password'),
                                                     request)
        return ok(auth_result)
    except ApplicationErrorException as ex:
        return bad_request(ex.http_message)


@api_view(['GET'])
@permission_classes([])
def resend_verification_code(request, user_id):
    # try:
    #
    #     user = Businessman.objects.get(id=user_id)
    #
    #     verify_code = user.verificationcodes
    #
    # except ObjectDoesNotExist:
    #     return Response(status=status.HTTP_404_NOT_FOUND)
    #
    # if verify_code.num_requested == 3:
    #
    #     return Response(status=status.HTTP_403_FORBIDDEN)
    #
    # verify_code.num_requested += 1
    #
    # verify_code.save()
    #
    # # code = verify_code.code
    #
    # SystemSMSMessage().send_verification_code(user.phone, verify_code.code)
    #
    # return Response(status=status.HTTP_200_OK)

    result = VerificationCodes().try_resend_verification_code(user_id)
    if not result[0] or (result[0] and not result[1]):
        return not_found()
    if result[0] and result[1] and not result[2]:
        return dependency_failed()
    return no_content()


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

    result = businessman_service.login_user(serializer.validated_data.get('username'),
                                            serializer.validated_data.get('password'), request)

    if result is None:
        return Response({'details': ['username or password is wrong']}, status=status.HTTP_401_UNAUTHORIZED)
    return ok(result)


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
        result = businessman_service.get_access_token_by_username(username)
        return ok(result)
    except ApplicationErrorException as ex:
        return bad_request(ex.http_message)


@api_view(['PUT'])
@permission_classes([])
def verify_user(request, businessman_id, code):
    try:
        businessman_service.verify_businessman_phone(businessman_id, code)

    except ApplicationErrorException as e:
        return bad_request(e.http_message)

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


@api_view(['GET'])
@permission_classes([])
def get_top5_categories_and_username_phone_email_exists(request):
    category_name = request.query_params.get('cname')
    serializer = CategorySerializer(BusinessCategory.get_top5_category(category_name), many=True)
    return ok(serializer.data)


@api_view(['GET'])
@permission_classes([])
def exists(request: Request):
    email = request.query_params.get('email')
    uname = request.query_params.get('uname')
    phone = request.query_params.get('phone')
    result = Businessman().username_phone_email_exists(uname, email, phone)
    return ok({'uname': result[0], 'email': result[1], 'phone': result[2]})
