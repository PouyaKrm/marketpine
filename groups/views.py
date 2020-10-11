from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.conf import settings
from rest_framework import generics, mixins, permissions
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.views import APIView

from common.util import create_detail_error
from common.util.http_helpers import ok, bad_request
from customers.serializers import CustomerListCreateSerializer
from .models import BusinessmanGroups
from .serializers import BusinessmanGroupsCreateListSerializer, BusinessmanGroupsRetrieveSerializer, CustomerSerializer
from .permissions import CanDeleteGroup, HasValidDefinedGroups

# Create your views here.

page_size = settings.PAGINATION_PAGE_NUM

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


class GroupMembersAPIView(APIView):

    def get(self, request, group_id):
        paginator = PageNumberPagination()
        paginator.page_size = page_size
        try:
            g = BusinessmanGroups.get_group_by_id(self.request.user, group_id)
            members = g.get_all_customers()
            page = paginator.paginate_queryset(members, self.request)
            sr = CustomerSerializer(page, context={'user', request.user}, many=True)
            return paginator.get_paginated_response(sr.data)
        except ObjectDoesNotExist:
            return bad_request(create_detail_error('invalid id'))

