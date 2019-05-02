from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate
from .message import SMSMessage
from .serializers import SalespersonRegisterSerializer, SalesmanRetrieveSerializer, SalesmanPasswordResetSerializer, SalesmanForgetPasswordSerializer
from .models import Salesman, VerificationCodes
# Create your views here.


class RegisterSalesmanView(generics.CreateAPIView):

    permission_classes = []
    authentication_classes = []
    serializer_class = SalespersonRegisterSerializer
    queryset = Salesman.objects.all()


@api_view(['POST'])
def create_user(request):

    """
    Registers new users or salesman. It Needs to be activated by the admin to be able to login
    """

    serializer = SalespersonRegisterSerializer(data=request.data)

    if not serializer.is_valid():

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = serializer.save()

    return Response(data={'id': user.id}, status=status.HTTP_201_CREATED)




@api_view(['GET'])
def resend_verification_code(request, user_id):

    try:

        user = Salesman.objects.get(id=user_id)

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





@api_view(['PUT'])
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
@permission_classes([permissions.IsAuthenticated])
def reset_user_password(request):

    """
    Resets the password of the user. Needs JWT token
    """

    serializer = SalesmanPasswordResetSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    user = authenticate(username=request.user.username, password=request.data.get('old_password'))
    if user is None:
        return Response(status=status.HTTP_403_FORBIDDEN)

    serializer.update(request.user, serializer.validated_data)

    return Response(status=status.HTTP_204_NO_CONTENT)






@api_view(['PUT'])
def user_forget_password(request):

    serializer = SalesmanForgetPasswordSerializer(data=request.data)

    if not serializer.is_valid():

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:

        user = Salesman.objects.get(username=request.data['username'], phone=request.data['phone'])

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



    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):

        serializer = SalesmanRetrieveSerializer(data=request.data)

        serializer._context = {'request': self.request}

        if not serializer.is_valid():

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = Salesman.objects.get(id=self.request.user.id)

        serializer.update(user, serializer.validated_data)

        serializer.instance = user

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):

        serializer = SalesmanRetrieveSerializer(self.request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

