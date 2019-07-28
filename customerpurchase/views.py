from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from customerpurchase.models import CustomerPurchase
from .serializers import PurchaseCreationUpdateSerializer, PurchaseListSerializer
from common.util import paginators
# Create your views here.


class PurchaseListCreateAPIView(APIView):


    def get(self, request):

        purchases = request.user.customerpurchase_set.all()

        # serializer = PurchaseListSerializer(purchases, many=True)

        paginate = paginators.NumberedPaginator(request, purchases, PurchaseListSerializer)

        return paginate.next_page()

    def post(self, request):
        serializer = PurchaseCreationUpdateSerializer(data=request.data)

        serializer._context = {'user': request.user}

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        obj = serializer.create(serializer.validated_data)

        serializer.instance = obj

        return Response(serializer.data, status=status.HTTP_200_OK)





class CustomerPurchaseUpdateDeleteAPIView(APIView):

    def put(self, request, purchase_id):

        try:
            purchase = CustomerPurchase.objects.get(id=purchase_id)
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = PurchaseCreationUpdateSerializer(data=request.data)

        serializer._context = {'user': request.user}

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        obj = serializer.update(purchase, serializer.validated_data)

        serializer.instance = obj

        return Response(serializer.data, status=status.HTTP_200_OK)


    def delete(self, request, purchase_id):

        try:
            request.user.customerpurchase_set.get(id=purchase_id).delete()
        except ObjectDoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)
