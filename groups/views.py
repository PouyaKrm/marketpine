from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from rest_framework import generics, mixins, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import BusinessmanGroups
from .serializers import BusinessmanGroupsCreateListSerializer, BusinessmanGroupsRetrieveSerializer, CustomerSerializer


# Create your views here.


class BusinessmanGroupsListAPIView(generics.ListAPIView, mixins.CreateModelMixin):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BusinessmanGroupsCreateListSerializer

    def get_queryset(self):

        return BusinessmanGroups.objects.filter(businessman=self.request.user)

    def get_serializer_context(self):

        return {'user': self.request.user}

    def post(self, request, *args, **kwargs):
        return self.create(request, args, kwargs)


class BusinessmanGroupsUpdateAPIView(generics.UpdateAPIView, mixins.DestroyModelMixin):

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BusinessmanGroupsCreateListSerializer
    lookup_field = 'id'

    def get_object(self):
        obj = get_object_or_404(BusinessmanGroups, id=self.kwargs['id'], businessman=self.request.user)
        self.check_object_permissions(self.request, obj)
        return obj

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CustomerGroupRetrieveAPIView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):

        try:
            group = BusinessmanGroups.objects.get(businessman=request.user, id=kwargs['group_id'])
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = CustomerSerializer(group.customers, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):

        serializer = BusinessmanGroupsRetrieveSerializer(data=request.data)

        serializer._context = {'user': self.request.user}

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        group = BusinessmanGroups.objects.get(businessman=request.user, id=kwargs['group_id'])

        serializer.update(group, serializer.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, *args, **kwargs):

        serializer = BusinessmanGroupsRetrieveSerializer(data=request.data)

        serializer._context = {'user': request.user}

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        group = BusinessmanGroups.objects.get(businessman=request.user, id=kwargs['group_id'])

        for i in serializer.validated_data.get('customers'):
            group.customers.remove(i)

        group.save()

        return Response(status=status.HTTP_204_NO_CONTENT)
