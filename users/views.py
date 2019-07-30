from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate

from common.util import custom_login_payload
from .serializers import *
# Create your views here.

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

    serializer = BusinessmanLoginSerializer(data=request.data)

    if not serializer.is_valid():

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=request.data.get('username'), password=request.data.get('password'))

    if user is None or user.is_verified is False:

        return Response({'details': ['username or password is wrong']}, status=status.HTTP_401_UNAUTHORIZED)

    payload = custom_login_payload(user)

    payload['username'] = user.get_username()
    payload['business_name'] = user.business_name

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

