from django.core.exceptions import ObjectDoesNotExist
from kavenegar import APIException, HTTPException
from rest_framework import generics, mixins, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from users.models import Customer
from .serializers import SMSTemplateSerializer, SentSMSSerializer, SentSMSRetrieveForCustomer
from .models import SMSTemplate, SentSMS
from .permissions import HasSMSPanelPermission
from common.util import paginators, jalali


class SMSTemplateCreateListAPIView(generics.ListAPIView, mixins.CreateModelMixin):

    permission_classes = [permissions.IsAuthenticated, HasSMSPanelPermission]
    serializer_class = SMSTemplateSerializer

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_queryset(self):
        return SMSTemplate.objects.filter(businessman=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SMSTemplateRetrieveAPIView(generics.RetrieveAPIView, mixins.UpdateModelMixin,
                                 mixins.DestroyModelMixin):

    permission_classes = [permissions.IsAuthenticated, HasSMSPanelPermission]
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

    serializer = SentSMSSerializer(data=request.data)

    serializer._context = {'user': request.user, 'is_plain': True}

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        serializer.create(serializer.validated_data)
    except APIException as e:
        return Response({'status': e.status, 'detail': e.message}, status=e.status)
    except HTTPException:
        return Response({'detail': 'خطا در ارسال پیام'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, HasSMSPanelPermission])
def send_sms_by_template(request, template_id):

    try:
        template = SMSTemplate.objects.get(businessman=request.user, id=template_id)

    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    request.data['content'] = template.content

    serializer = SentSMSSerializer(data=request.data)

    serializer._context = {'user': request.user, 'is_plain': False}

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    serializer.create(serializer.validated_data)

    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_businessman_sent_sms(request):

    # serializer = SentSMSSerializer(SentSMS.objects.filter(businessman=request.user).all(), many=True)
    # return Response(serializer.data, status=status.HTTP_200_OK)
        businessman_sentsms_list=SentSMS.objects.filter(businessman=request.user).all()
        paginate = paginators.NumberedPaginator(request, businessman_sentsms_list, SentSMSSerializer)
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

