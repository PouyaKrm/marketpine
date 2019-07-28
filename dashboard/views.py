from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response


@api_view(['GET'])
def customers_total(request: Request):

    return Response({'customers_total': request.user.customers.count()}, status=status.HTTP_200_OK)
