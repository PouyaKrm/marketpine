from django.shortcuts import render, get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Festival
from .serializers import FestivalCreationSerializer, FestivalListSerializer, RetrieveFestivalSerializer
# Create your views here.


class FestivalsListAPIView(generics.ListAPIView, mixins.CreateModelMixin):

    serializer_class = FestivalCreationSerializer

    def get_queryset(self):

        return Festival.objects.filter(businessman=self.request.user)

    def get_serializer_context(self):

        return {'user': self.request.user}

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class FestivalAPIView(APIView):

    def get(self, request):

        serializer = FestivalListSerializer(request.user.festival_set.all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):

        serializer = FestivalCreationSerializer(data=request.data)
        serializer._context = {'user': request.user}
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        obj = serializer.create(serializer.validated_data)
        serializer.instance = obj
        return Response(serializer.data, status=status.HTTP_200_OK)


class FestivalRetrieveAPIView(generics.RetrieveAPIView, mixins.UpdateModelMixin):

    serializer_class = RetrieveFestivalSerializer

    lookup_field = 'id'

    def get_object(self):

        fest = get_object_or_404(self.request.user.festival_set, id=self.kwargs['id'])
        self.check_object_permissions(self.request, fest)

        return fest


    def get_serializer_context(self):
        return {'user': self.request.user, 'festival_id': self.kwargs['id']}

    def put(self, request, *args, **kwargs):

        return self.update(request, *args, **kwargs)

