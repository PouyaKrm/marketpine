from django.core.exceptions import ObjectDoesNotExist
from common.util.kavenegar_local import APIException, HTTPException
from rest_framework import generics, mixins, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from users.models import Customer
from .serializers import SMSTemplateSerializer, SendSMSSerializer, SentSMSRetrieveForCustomer, SendPlainSMSToAllSerializer, SendByTemplateSerializer
from .models import SMSTemplate, SentSMS
from .permissions import HasSMSPanelPermission
from common.util import paginators, jalali

from .services import send_template_sms_message_to_all

from common.util.sms_panel.message import ClientBulkToAllSMSMessage


class SMSTemplateCreateListAPIView(generics.ListAPIView, mixins.CreateModelMixin):

    serializer_class = SMSTemplateSerializer

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_queryset(self):
        return SMSTemplate.objects.filter(businessman=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SMSTemplateRetrieveAPIView(generics.RetrieveAPIView, mixins.UpdateModelMixin,
                                 mixins.DestroyModelMixin):

    serializer_class = SMSTemplateSerializer

    def get_queryset(self):
        return SMSTemplate.objects.filter(businessman=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_serializer_context(self):
        return {'user': self.request.user}


@api_view(['POST'])
def send_plain_sms(request):

    """
    sends sms message without using template.
    :param request: contains message content and id of customers that are receptors of message
    :return: If data is invalid, Response with status code 400, else if error
    was occurred in kavenegar api, returns Response with a message from SMS API with error message
    other that 400.  With status code 500 if other error occurred.
     If operation was successful, Response with status code 204
    """

    serializer = SendSMSSerializer(data=request.data, context={'user': request.user})

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        serializer.create(serializer.validated_data)
    except APIException as e:
        return Response({'status': e.status, 'detail': e.message}, status=status.HTTP_424_FAILED_DEPENDENCY)
    except HTTPException:
        return Response({'detail': 'خطا در ارسال پیام'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def send_plain_to_all(request):

    """
    sends a same message to all customers of a businessman.
    :return: If data is invalid, Response with status code 400, else if error
    was occurred in kavenegar api, returns Response with a message from SMS API with error message
    other that 400.  With status code 500 if other error occurred.
     If operation was successful, Response with status code 204
    """

    serializer = SendPlainSMSToAllSerializer(data=request.data, context={'user': request.user})

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    try:
        serializer.create(serializer.validated_data)
    except APIException as e:
        return Response({'status': e.status, 'detail': e.message}, status=status.HTTP_424_FAILED_DEPENDENCY)
    except HTTPException:
        return Response({'detail': 'خطا در ارسال پیام'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=204)

@api_view(['POST'])
def send_sms_by_template(request, template_id):

    """
    sends message to specific number of cutomers of a businessman using a tmplate that it's id 
    is specified as a path variable.
    """

    try:
        template = SMSTemplate.objects.get(businessman=request.user, id=template_id)

    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = SendByTemplateSerializer(data=request.data, context={'user': request.user, 'template': template})

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        serializer.create(serializer.validated_data)
    except APIException as e:
        return Response({'status': e.status, 'detail': e.message}, status=status.HTTP_424_FAILED_DEPENDENCY)
    except HTTPException as e:
        return Response({'detail': 'خطا درپردازش اطلاعات'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def send_sms_by_template_to_all(request, template_id):

    """
    sends sms message to all customers of a businessman by a template specified as path varialble
    """

    try:
        template = SMSTemplate.objects.get(businessman=request.user, id=template_id)
    except ObjectDoesNotExist:
        return Response({'detail': ' قالب مورد نظر وجود ندارد'}, status=status.HTTP_404_NOT_FOUND)

    try:
        send_template_sms_message_to_all(request.user, template.content)
    except APIException as e:
        return Response({'status': e.status, 'detail': e.message}, status=status.HTTP_424_FAILED_DEPENDENCY)

    return Response(status=status.HTTP_204_NO_CONTENT)
    


@api_view(['GET'])
def get_businessman_sent_sms(request):

    # serializer = SentSMSSerializer(SentSMS.objects.filter(businessman=request.user).all(), many=True)
    # return Response(serializer.data, status=status.HTTP_200_OK)
        businessman_sentsms_list=SentSMS.objects.filter(businessman=request.user).all()
        paginate = paginators.NumberedPaginator(request, businessman_sentsms_list, SendSMSSerializer)
        return paginate.next_page()


@api_view(['GET'])
def get_customer_sent_sms(request, customer_id):

    try:
        customer = Customer.objects.get(businessman=request.user, id=customer_id)

    except ObjectDoesNotExist:
        return Response({'details': ['customer does not exist']}, status=status.HTTP_404_NOT_FOUND)

    sms = customer.sentsms_set.all()

    serializer = SentSMSRetrieveForCustomer(sms.all(), many=True)

    serializer._context = {'customer': customer}

    return Response(serializer.data, status=status.HTTP_200_OK)

