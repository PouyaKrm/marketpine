from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.request import Request
from rest_framework.views import APIView

from panelsetting.models import PanelSetting
from .serializers import PanelSettingSerializer
from .permissions import CreatePanelSettingIfDoesNotExist

class RetrieveUpdatePanelSettingApiView(APIView):

    """
    Retrieves and updates data of the panel setting
    """

    permission_classes = [permissions.IsAuthenticated, CreatePanelSettingIfDoesNotExist]

    def get(self, request: Request):

        """
        Represent current settings of the panel of the authenticated user
        :param request: Contains data of the request
        :return: Response with body of the current settings and 200 status code
        """

        serializer = PanelSettingSerializer(request.user.panelsetting)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request: Request):

        """
        Updates Setting of the panel
        :param request: Contains data of the request
        :return: If new data for settings is invalid Returns Response with error messages and 400 status code, Else
        Response with body of the new settings and 200 status code
        """

        serializer = PanelSettingSerializer(data=request.data)

        serializer._context = {'user': request.user}

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        obj = serializer.update(request.user.panelsetting, serializer.validated_data)

        serializer.instance = obj

        return Response(serializer.data, status=status.HTTP_200_OK)

