from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from common.util.http_helpers import not_found, no_content
from customer_return_plan.loyalty.services import loyalty_service
from customerpurchase.models import CustomerPurchase
from customers.services import customer_service
from .serializers import PurchaseCreationUpdateSerializer, PurchaseListSerializer, CustomerPurchaseListSerializer
from common.util import paginators
# Create your views here.

from .services import purchase_service

class PurchaseListCreateAPIView(APIView):


    def get(self, request):

        purchases = purchase_service.get_businessman_all_purchases(request.user)

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

        serializer = PurchaseCreationUpdateSerializer(data=request.data, context={'user': request.user})

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        obj = serializer.update(purchase, serializer.validated_data)

        serializer.instance = obj

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, purchase_id):

        # try:
        #     purchase = request.user.customerpurchase_set.get(id=purchase_id)
        # except ObjectDoesNotExist:
        #     return Response(status=status.HTTP_404_NOT_FOUND)
        # loyalty_service.re_evaluate_discounts_after_purchase_update_or_delete(request.user, purchase.customer)
        # return Response(status=status.HTTP_204_NO_CONTENT)
        result = purchase_service.delete_purchase_by_purchase_id(request.user, purchase_id)
        if not result[0]:
            return not_found()
        return no_content()


@api_view(['GET'])
def get_customer_purchases(request: Request, customer_id):

    customer = customer_service.get_customer_by_id_or_404(request.user, customer_id)
    try:
        customer_purchases = purchase_service.get_customer_all_purchases(request.user, customer)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    paginate = paginators.NumberedPaginator(request, customer_purchases, CustomerPurchaseListSerializer)

    return paginate.next_page()
