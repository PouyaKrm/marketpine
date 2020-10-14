from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import generics, mixins, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from base_app.views import BaseListAPIView
from common.util.http_helpers import ok, bad_request, not_found, forbidden, no_content
from customer_return_plan.festivals.permissions import CanDeleteOrUpdateFestival
from customer_return_plan.festivals.services import FestivalService
from smspanel.services import SendSMSMessage
from users.models import Customer
from .models import Festival
from .serializers import FestivalCreationSerializer, FestivalListSerializer, RetrieveFestivalSerializer, \
    FestivalCustomerSerializer
from common.util import generate_discount_code, DiscountType, create_detail_error
from common.util import paginators

from customers.serializers import CustomerListCreateSerializer

from smspanel.permissions import HasValidCreditSendSMSToAll, HasActiveSMSPanel


# Create your views here.

festival_service = FestivalService()


class FestivalsListAPIView(BaseListAPIView, mixins.CreateModelMixin):
    serializer_class = FestivalCreationSerializer
    permission_classes = [permissions.IsAuthenticated, HasActiveSMSPanel]

    def get_queryset(self):
        return festival_service.get_businessman_all_undeleted_festivals(businessman=self.request.user)

    def get_serializer_context(self):
        return {'user': self.request.user}

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class FestivalAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasActiveSMSPanel]

    def get(self, request):

        """
        NEW(start_date, end_date, discount_code fields are added)
        List all registered festivals.
        parameter : q: if provided all festivals that their discount code is like represented value will be list to output
        :param request:
        :return: Response with list of festivals and as body and status 200
        """
        q = request.query_params.get('q')

        if q is not None:
            # result_set = request.user.festival_set.filter(discount_code__contains=q).all()
            result_set = festival_service.get_businessman_festivals_filtered_by_discount_code(request.user, q)
        else:
            # result_set = request.user.festival_set.all()
            result_set = festival_service.get_businessman_all_undeleted_festivals(request.user)

        # serializer = FestivalListSerializer(result_set, many=True)
        # return Response(serializer.data, status=status.HTTP_200_OK)

        paginate = paginators.NumberedPaginator(request, result_set, FestivalListSerializer)
        return paginate.next_page()

    def post(self, request: Request):

        """
        NEW(message field is added)
        Creates new Festival
        parameter : auto: if True generates a discount code automatically. else, the client must enter discount code
        :param request:
        :return:
        """

        auto = request.query_params.get('auto')
        if (auto is not None) and auto.lower() == 'true':
            request.data['discount_code'] = generate_discount_code(DiscountType.FESTIVAL)

        serializer = FestivalCreationSerializer(data=request.data)

        serializer._context = {'user': request.user}
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        obj = serializer.create(serializer.validated_data)
        serializer.instance = obj

        serializer.instance = obj

        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@permission_classes([permissions.IsAuthenticated, HasActiveSMSPanel, HasValidCreditSendSMSToAll])
def send_festival_message(request: Request, festival_id):
    """
    NEW
    Sends messages to all customer of the user to inform them about festival if messages are not sent before
    :param request:
    :param festival_id: id of the festival that message belongs to
    :return: Response with 204 status code if operation was successful else if festival messages already sent
    or festival is expired Response with a message and 403 status code will be returned
    """

    # try:
    #     festival = request.user.festival_set.get(id=festival_id)
    # except ObjectDoesNotExist:
    result = festival_service.send_festival_message_by_festival_id_if_festival_is_not_deleted_expired_message_sent(request.user, festival_id)
    if not result[0]:
        return not_found()

    if result[0] and not result[1]:
        return forbidden(create_detail_error('پیام های مربوط به این جشنواره قبلا فرستاده شده یا تاریخ جشنواره به اتمام رسیده'))

    return no_content()


class FestivalRetrieveAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, CanDeleteOrUpdateFestival]

    def get(self, request, id):
        fest = get_object_or_404(request.user.festival_set, id=id)
        serializer = RetrieveFestivalSerializer(instance=fest)
        return ok(serializer.data)

    def get_serializer_context(self):
        return {'user': self.request.user, 'festival_id': self.lookup_field}

    def put(self, request, id):
        fest = get_object_or_404(request.user.festival_set, id=id)
        serializer = RetrieveFestivalSerializer(data=request.data, instance=fest,
                                                context={'user': request.user,
                                                         'discount_instance': fest.discount}
                                                )
        if not serializer.is_valid():
            return bad_request(serializer.errors)
        serializer.update(fest, serializer.validated_data)
        return ok(serializer.data)

    def delete(self, request, id):
        result = festival_service.delete_festival_by_festival_id(request.user, id)
        if not result[0]:
            return not_found(create_detail_error('آیدی جشنواره اشتباه است'))

        serializer = RetrieveFestivalSerializer(result[1])
        return ok(serializer.data)


@api_view(['GET'])
def list_customers_in_festival(request, festival_id):
    try:
        festival = request.user.festival_set.get(id=festival_id)
    except ObjectDoesNotExist:
        return Response({'details': ['این جشنواره وجود ندارد']}, status=status.HTTP_404_NOT_FOUND)

    paginator = paginators.NumberedPaginator(request, festival.customers.all(), CustomerListCreateSerializer)

    return paginator.next_page()


@api_view(['POST'])
def add_customer_to_festival(request):
    serializer = FestivalCustomerSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        customer = request.user.customers.get(phone=request.data['customer_phone'])
    except ObjectDoesNotExist:
        return Response({'details': ['این مشتری در لیست مشتریان شما نیست']}, status=status.HTTP_404_NOT_FOUND)

    try:
        festival = request.user.festival_set.get(discount_code=serializer.data['discount_code'])
    except ObjectDoesNotExist:
        return Response({'details': ['جشنواره با این کد تخفیف وجود ندارد']}, status=status.HTTP_404_NOT_FOUND)

    if festival.customers.filter(phone=customer.phone).exists():
        return Response({'details': ['این جشنواره توسط این مشتری استفاده شده است']}, status=status.HTTP_403_FORBIDDEN)
    elif festival.end_date <= timezone.now().date():
        return Response({'details': ['تاریخ جشنواره به اتمام رسیده']}, status=status.HTTP_403_FORBIDDEN)

    festival.customers.add(customer)
    festival.save()
    return Response({'details': ['customers added to festival']}, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_customer_from_festival(request, festival_id, customer_id):
    try:
        festival = request.user.festival_set.get(id=festival_id)
    except ObjectDoesNotExist:
        return Response({'details': ['این جشنواره وجود ندارد']}, status=status.HTTP_404_NOT_FOUND)
    try:
        customer = Customer.objects.get(id=customer_id)
    except ObjectDoesNotExist:
        return Response({'details': ['مشتری با این آیدی ثبت نشده']}, status=status.HTTP_404_NOT_FOUND)
    festival.customers.remove(customer)
    festival.save()
    return Response(status=status.HTTP_204_NO_CONTENT)
