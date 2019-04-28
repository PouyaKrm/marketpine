from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.contrib.auth import authenticate

from .message import Message
from .serializers import SalespersonRegisterSerializer, SalesmanSerializer, SalesmanPasswordResetSerializer
from .models import Salesman
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
def get_verification_code(request, user_id):

    try:

        user = Salesman.objects.get(id=user_id)

        verify_code = user.verificationcodes

    except:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if verify_code.num_requested == 3:

        return Response(status=status.HTTP_403_FORBIDDEN)

    verify_code.num_requested += 1

    verify_code.save()

    # code = verify_code.code

    Message().send_verification_code(user.phone, verify_code.code)

    return Response(status=status.HTTP_200_OK)



@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated])
def salesman_reset_password(request):

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


class SalesmanAPIView(APIView):

    """
    put:
    Updates the profile of the user. Needs JWT token

    get:
    Retrieves the profile data Including phone, business_name, first_name, last_name, email.
     but phone number and business name are required. Needs JWT toeken
    """



    permission_classes = [permissions.IsAuthenticated]

    def put(self, request, *args, **kwargs):

        serializer = SalesmanSerializer(data=request.data)

        serializer._context = {'request': self.request}

        if not serializer.is_valid():

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = Salesman.objects.get(id=self.request.user.id)

        serializer.update(user, serializer.validated_data)

        serializer.instance = user

        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, *args, **kwargs):

        serializer = SalesmanSerializer(self.request.user)

        return Response(serializer.data, status=status.HTTP_200_OK)

