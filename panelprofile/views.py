from django.contrib.auth import authenticate
from django.shortcuts import render

# Create your views here.
from kavenegar import APIException
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response

from panelprofile.serializers import SMSPanelCreateSerializer


@api_view(['POST'])
def take_authenticate_documents(request: Request):

    serializer = SMSPanelCreateSerializer(data=request.data)

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

    return  Response(status=status.HTTP_204_NO_CONTENT)
