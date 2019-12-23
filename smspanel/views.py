from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.conf import settings
from django.urls import reverse

from common.util import create_link
from common.util.paginators import create_pagination_response
from common.util.kavenegar_local import APIException, HTTPException
from common.util.sms_panel.message import retrive_sent_messages
from common.util import paginators as custom_paginator

from rest_framework import generics, mixins, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from users.models import Customer, Businessman
from .serializers import SMSTemplateSerializer, SendSMSSerializer, SentSMSRetrieveForCustomer, SendPlainSMSToAllSerializer, SendByTemplateSerializer, SendPlainToGroup, UnsentPlainSMSListSerializer, UnsentTemplateSMSListSerializer
from .models import SMSTemplate, SentSMS
from .permissions import HasValidCreditSendSMS, HasValidCreditSendSMSToAll, HasValidCreditResendPlainSMS, HasValidCreditResendTemplateSMS, HasValidCreditSendSMSToGroup
from common.util import paginators, jalali

from .helpers import send_template_sms_message_to_all, SendSMSMessage

from common.util.sms_panel.message import ClientBulkToAllSMSMessage

page_size = settings.PAGINATION_PAGE_NUM
api_key = settings.SMS_PANEL['API_KEY']




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
@permission_classes([permissions.IsAuthenticated, HasValidCreditSendSMS])
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
        return Response({'detail': 'خطا در ارسال پیام'}, status=status.HTTP_424_FAILED_DEPENDENCY)

    return Response(status=status.HTTP_204_NO_CONTENT)





@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, HasValidCreditSendSMSToAll])
def send_plain_to_all(request):

    """
    sends a same message to all customers of a businessman.
    :return: If data is invalid, Response with status code 400, else if error
    was occurred in kavenegar api, returns Response with a message from SMS API with error message
    other that 400.  With status code 424 if other error occurred.
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
        return Response({'detail': 'خطا در ارسال پیام'}, status=status.HTTP_424_FAILED_DEPENDENCY)

    return Response(status=204)





@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, HasValidCreditSendSMS])
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
@permission_classes([permissions.IsAuthenticated, HasValidCreditSendSMSToAll])
def send_sms_by_template_to_all(request, template_id):

    """
    sends sms message to all customers of a businessman by a template specified as path varialble
    """

    try:
        template = SMSTemplate.objects.get(businessman=request.user, id=template_id)
    except ObjectDoesNotExist:
        return Response({'detail': ' قالب مورد نظر وجود ندارد'}, status=status.HTTP_404_NOT_FOUND)

    messainger = SendSMSMessage()

    try:
        messainger.send_by_template_to_all(request.user, template.content)
    except APIException as e:
        return Response({'status': e.status, 'detail': e.message}, status=status.HTTP_424_FAILED_DEPENDENCY)

    return Response(status=status.HTTP_204_NO_CONTENT)
    




@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, HasValidCreditSendSMSToGroup])
def send_plain_sms_to_group(request: Request, group_id):


    user = request.user

    try:
        group = user.businessmangroups_set.get(id=group_id)
    except ObjectDoesNotExist:
        return Response({'details': 'group not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = SendPlainToGroup(data=request.data, context={'user': request.user, 'group': group})


    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        serializer.create(serializer.validated_data)
    except APIException as e:
        return Response({'status': e.status, 'message': e.message}, status=status.HTTP_424_FAILED_DEPENDENCY)

    return Response(status=status.HTTP_204_NO_CONTENT)





@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, HasValidCreditSendSMSToGroup])
def send_template_sms_to_group(request: Request, template_id, group_id):
    
    try:
        group = request.user.businessmangroups_set.get(id=group_id)
    except ObjectDoesNotExist:
        return Response({'details': 'گروه وجود ندارد'}, status=status.HTTP_404_NOT_FOUND)
    
    try:
        template = SMSTemplate.objects.get(businessman=request.user, id=template_id)
    except ObjectDoesNotExist:
        return Response({'detail': ' قالب مورد نظر وجود ندارد'}, status=status.HTTP_404_NOT_FOUND)
    
    messagger = SendSMSMessage()

    try:
        messagger.send_by_template(request.user, group.customers.all(), template.content)
    except APIException as e:
        return Response({'status': e.status, 'message': e.message}, status=status.HTTP_424_FAILED_DEPENDENCY)
    return Response(status=status.HTTP_204_NO_CONTENT)





@api_view(['GET'])
def list_unsent_plain_sms(request):

    """
    retrieves unsent plain sms 
    """

    unsent_sms = request.user.unsentplainsms_set.order_by('-create_date').all()

    paginate = custom_paginator.NumberedPaginator(request, unsent_sms, UnsentPlainSMSListSerializer)

    return paginate.next_page()





@api_view(['GET'])
def list_unsent_template_sms(request: Request):

    unsent_sms = request.user.unsenttemplatesms_set.order_by('-create_date').all()

    paginate = custom_paginator.NumberedPaginator(request, unsent_sms, UnsentTemplateSMSListSerializer)

    return paginate.next_page()





@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, HasValidCreditResendPlainSMS])
def resend_plain_sms(request: Request, unsent_sms_id):

    try:
        unsent_plain_sms = request.user.unsentplainsms_set.get(id=unsent_sms_id)
    except ObjectDoesNotExist:
        return Response({'detail': 'unsent sms with provided id does not exist'}, status=status.HTTP_404_NOT_FOUND)
    

    messainger = SendSMSMessage()

    try:
        messainger.resend_unsent_plain_sms(request.user, unsent_plain_sms)
    except APIException as e:
        return Response({'status': e.status, 'message': e.message}, status=status.HTTP_424_FAILED_DEPENDENCY)

    return Response(status=status.HTTP_204_NO_CONTENT)






@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, HasValidCreditResendTemplateSMS])
def resend_template_sms(request: Request, unsent_sms_id):

    try:
        unsent_template_sms = request.user.unsenttemplatesms_set.get(id=unsent_sms_id)
    except ObjectDoesNotExist:
        return Response({'detail': 'unsent sms with provided id does not exist'}, status=status.HTTP_404_NOT_FOUND)
    
    messainger = SendSMSMessage()

    try:
        messainger.resend_unsent_template_sms(request.user, unsent_template_sms)
    except APIException as e:
        return Response({'status': e.status, 'message': e.message}, status=status.HTTP_424_FAILED_DEPENDENCY)

    return Response(status=status.HTTP_204_NO_CONTENT)






@api_view(['GET'])
def get_businessman_sent_sms(request: Request):

    count = SentSMS.objects.filter(businessman=request.user).count()
    p = Paginator(SentSMS.objects.filter(businessman=request.user).all(), page_size)

    retrieve_link = create_link(reverse('sent_sms_retrieve'), request)

    try:
        page_num = int(request.query_params.get('page'))
    except ValueError:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if page_num is not None:
        if p.num_pages < page_num or page_num <= 0:
            return Response({'detail': 'page does not exist'}, status=status.HTTP_404_NOT_FOUND)

        result = retrive_sent_messages(request.user.smspanelinfo.api_key, [str(m.message_id) for m in p.page(page_num).object_list])
        try:
            return create_pagination_response(p.page(page_num), result, count, retrieve_link, request)
        except APIException as e:
            return Response({'status': e.status, 'message': e.message}, status=status.HTTP_424_FAILED_DEPENDENCY)
    
    elif p.count == 0:
        return create_pagination_response(page, [], 0, retrieve_link, request)

    else:
        result = retrive_sent_messages(request.user.smspanelinfo.api_key, [str(m.message_id) for m in p.page(1).object_list])
        try:
            return create_pagination_response(p.page(1), result, count, retrieve_link, request)
        except APIException as e:
            return Response({'status': e.status, 'message': e.message}, status=status.HTTP_424_FAILED_DEPENDENCY)




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
