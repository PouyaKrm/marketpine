from coreapi import Field
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework import generics, mixins, status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.schemas import AutoSchema
from rest_framework.views import APIView
from users.models import Customer
from .models import Festival
from .serializers import FestivalCreationSerializer, FestivalListSerializer, RetrieveFestivalSerializer, \
    CustomerSerializer, FestivalCustomerSerializer
from common.util import generate_discount_code, paginators, DiscountType
from common.util.custom_templates import FestivalTemplate
from common.util.sms_message import FestivalMessageBulk


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

        """
        NEW(start_date, end_date, discount_code fields are added)
        List all registered festivals.
        parameter : q: if provided all festivals that their discount code is like represented value will be list to output
        :param request:
        :return: Response with list of festivals and as body and status 200
        """
        q = request.query_params.get('q')

        if q is not None:
            result_set = request.user.festival_set.filter(discount_code__contains=q).all()
        else:
            result_set = request.user.festival_set.all()

        serializer = FestivalListSerializer(result_set, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

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


@api_view(['PATCH'])
def send_festival_message(request: Request, festival_id):

    """
    NEW
    Sends messages to all customer of the user to inform them about festival if messages are not sent before
    :param request:
    :param festival_id: id of the festival that message belongs to
    :return: Response with 204 status code if operation was successful else if festival messages already sent
    or festival is expired Response with a message and 403 status code will be returned
    """

    try:
        festival = request.user.festival_set.get(id=festival_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if festival.messages_sent or festival.end_date <= timezone.now().date():

        return Response({'details': ['پیام های مربوط به این جشنواره قبلا فرستاده شده یا تاریخ جشنواره به اتمام رسیده']},
                        status=status.HTTP_403_FORBIDDEN)

    template = FestivalTemplate(request.user, festival)

    rendered_messages = template.get_message_phone_lists()

    sms = FestivalMessageBulk(rendered_messages['phones'], rendered_messages['messages'])

    sms.send_bulk()

    festival.messages_sent = True
    festival.save()

    return Response(status=status.HTTP_204_NO_CONTENT)


class FestivalRetrieveAPIView(generics.RetrieveAPIView, mixins.UpdateModelMixin, mixins.DestroyModelMixin):

    serializer_class = RetrieveFestivalSerializer

    lookup_field = 'id'

    def get_object(self):

        fest = get_object_or_404(self.request.user.festival_set, id=self.kwargs['id'])
        self.check_object_permissions(self.request, fest)

        return fest

    def get_serializer_context(self):
        return {'user': self.request.user, 'festival_id': self.lookup_field}

    def put(self, request, *args, **kwargs):

        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


@api_view(['GET'])
def list_customers_in_festival(request, festival_id):

    try:
        festival = request.user.festival_set.get(id=festival_id)
    except ObjectDoesNotExist:
        return Response({'details': ['این جشنواره وجود ندارد']}, status=status.HTTP_404_NOT_FOUND)

    paginator = paginators.NumberedPaginator(request, festival.customers.all(), CustomerSerializer)

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


@api_view(['GET'])
def check_festival_name_or_discount_code_exists(request: Request):


    """
    NEW - use this method when user is registering a festival.
    To Check that festival name or discount code already exist Use This method.
    one of the parameters are optional. but if none of them are presented Response
    with 400 status code will be returned.
    parameter : name: name of the festival. - code: discount code of the festival
    :param request:
    :return:
    """
    code = request.query_params.get('code')
    name = request.query_params.get('name')
    payload = {}

    if (name is None) and (code is None):
        return Response({'details': ['name and code parameters are required']}, status=status.HTTP_400_BAD_REQUEST)

    if (name is not None) and (request.user.festival_set.filter(name=name).exists()):
        payload['name'] = ['این نام قبلا ثبت شده']

    if (code is not None) and (request.user.festival_set.filter(discount_code=code).exists()):
        payload['discount_code'] = ['این کد تخفیف قبلا ثبت شده']

    if len(payload) == 0:
        return Response(status=status.HTTP_404_NOT_FOUND)
    else:
        return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_festival_by_discount_code(request: Request, discount_code):

    """
    NEW
    Retrieves specific festival by it's discount code
    :param request: Contains data of the request
    :param discount_code: discount code of the festival that is provided by the user
    :return: If festival exists return Response with festival data as body and 200 status code.
    Else Response with 404 status code.
    """

    try:
        festival = request.user.festival_set.get(discount_code=discount_code)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = RetrieveFestivalSerializer(festival)

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_number_of_festivals(request: Request):
    """
    NEW
    Represents number of festivals that is registered by the user
    :param request:
    :return: Response with total festivals number as body and 200 status code
    """
    return Response({'festivals_total': request.user.festival_set.count()}, status=status.HTTP_200_OK)
