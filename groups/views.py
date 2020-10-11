from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, mixins, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import BusinessmanGroups
from .serializers import BusinessmanGroupsCreateListSerializer, BusinessmanGroupsRetrieveSerializer
from .permissions import CanDeleteGroup
from common.util import paginators

# Create your views here.


class BusinessmanGroupsListCreateAPIView(generics.ListAPIView, mixins.CreateModelMixin):

    """
    Lists and create group for the user
    """
    serializer_class = BusinessmanGroupsCreateListSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated]

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

    serializer_class = BusinessmanGroupsRetrieveSerializer
    lookup_field = 'id'
    permission_classes = [permissions.IsAuthenticated, CanDeleteGroup]

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_object(self):
        obj = get_object_or_404(BusinessmanGroups, id=self.kwargs['id'], businessman=self.request.user)
        self.check_object_permissions(self.request, obj)
        return obj

    def put(self, request: Request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
