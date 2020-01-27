from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, mixins, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import BusinessmanGroups
from .serializers import BusinessmanGroupsCreateListSerializer, BusinessmanGroupsRetrieveSerializer, CustomerSerializer
from .permissions import HasValidDefinedGroups
from common.util import paginators

# Create your views here.


class BusinessmanGroupsListCreateAPIView(generics.ListAPIView, mixins.CreateModelMixin):

    """
    Lists and create group for the user
    """
    serializer_class = BusinessmanGroupsCreateListSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated, HasValidDefinedGroups]

    def get_queryset(self):

        return BusinessmanGroups.objects.filter(businessman=self.request.user)

    def get_serializer_context(self):

        return {'user': self.request.user}

    def post(self, request, *args, **kwargs):
        return self.create(request, args, kwargs)


class BusinessmanGroupsUpdateAPIView(generics.RetrieveAPIView, mixins.UpdateModelMixin, mixins.DestroyModelMixin):

    """
    NEW
    Retrieves info of specific group y it's id. Updates info of the group like group title. Also deletes a group by it's id
    """

    serializer_class = BusinessmanGroupsCreateListSerializer
    lookup_field = 'id'

    def get_object(self):
        obj = get_object_or_404(BusinessmanGroups, id=self.kwargs['id'], businessman=self.request.user)
        self.check_object_permissions(self.request, obj)
        return obj

    def put(self, request: Request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CustomerGroupRetrieveAPIView(APIView):

    """
    List customers that are the members of the group, Also adds and removes members from group.
    """
    def get(self, request, *args, **kwargs):
        """
        Lists customers that are members of the group
        :param request:
        :param args:
        :param kwargs:
        :return: Response with list of the customers and 200 status code. Else Response with status code 404
        """
        try:
            group = BusinessmanGroups.objects.get(businessman=request.user, id=kwargs['group_id'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # serializer = CustomerSerializer(group.customers, many=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)

        paginate = paginators.NumberedPaginator(request, group.customers, CustomerSerializer)
        return paginate.next_page()

    def put(self, request, *args, **kwargs):

        """
        Adds member to the group by the list of ids of the customers that is sent as the body of the request.
        If a member already exists it will be ignored by add method.
        :param request: Contains data of the request
        :param args:
        :param kwargs:
        :return: Response with status code 204 if operation is successful.
        Response with 400 satus code and error messages if sent data is invalid.
        Response with status code 404 if group does not exist
        """

        serializer = BusinessmanGroupsRetrieveSerializer(data=request.data)

        serializer._context = {'user': self.request.user}

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        group = BusinessmanGroups.objects.get(businessman=request.user, id=kwargs['group_id'])

        serializer.update(group, serializer.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, *args, **kwargs):

        """
        Removes customers from the group by the list of customer ids that is sent as the body of the request.
        If a customer is already removed, it will be ignored y remove function
        :param request:
        :param args:
        :param kwargs:
        :return: Response with status code 204 if operation was successful.
        Response with 400 and error messages if sent data is invalid.
        Response with 404 if group does not exist.
        """

        serializer = BusinessmanGroupsRetrieveSerializer(data=request.data)

        serializer._context = {'user': request.user}

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        group = BusinessmanGroups.objects.get(businessman=request.user, id=kwargs['group_id'])

        for i in serializer.validated_data.get('customers'):
            group.customers.remove(i)

        group.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
