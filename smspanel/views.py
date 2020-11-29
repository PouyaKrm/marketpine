from django.core.exceptions import ObjectDoesNotExist
from django.core.paginator import Paginator
from django.conf import settings
from django.urls import reverse
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView

from base_app.views import BaseListAPIView
from common.util import create_link
from common.util.http_helpers import ok, get_query_param_or_default, bad_request
from common.util.paginators import create_pagination_response, create_pagination_response_body
from common.util.kavenegar_local import APIException, HTTPException
from common.util.sms_panel.message import retrive_sent_messages
from common.util import paginators as custom_paginator

from rest_framework import generics, mixins, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from users.models import Customer, Businessman
from .serializers import SMSTemplateSerializer, SendSMSSerializer, SentSMSRetrieveForCustomer, \
    SendPlainSMSToAllSerializer, SendByTemplateSerializer, SendPlainToGroup, UnsentPlainSMSListSerializer, \
    UnsentTemplateSMSListSerializer, SMSMessageListSerializer, WelcomeMessageSerializer
from .models import SMSTemplate, SentSMS, SMSMessage
from .permissions import HasValidCreditSendSMS, HasValidCreditSendSMSToAll, HasValidCreditResendFailedSMS, \
    HasValidCreditResendTemplateSMS, HasValidCreditSendSMSToGroup, HasActiveSMSPanel
from .serializers import SMSTemplateSerializer, SendSMSSerializer, SentSMSRetrieveForCustomer, SendPlainSMSToAllSerializer, SendByTemplateSerializer, SendPlainToGroup, UnsentPlainSMSListSerializer, UnsentTemplateSMSListSerializer
from .models import SMSTemplate, SentSMS
from common.util import paginators, jalali

from .services import send_template_sms_message_to_all, SendSMSMessage, sms_message_service

from common.util.sms_panel.message import ClientBulkToAllToCustomerSMSMessage

page_size = settings.PAGINATION_PAGE_NUM

def create_sms_sent_success_response(user: Businessman):
    return Response({'credit': user.smspanelinfo.credit}, status=status.HTTP_200_OK)

def send_message_failed_response(ex: APIException):
    return Response({'status': ex.status, 'message': ex.message}, status=status.HTTP_424_FAILED_DEPENDENCY)


class SMSTemplateCreateListAPIView(BaseListAPIView, mixins.CreateModelMixin):

    serializer_class = SMSTemplateSerializer
    pagination_class = None
    permission_classes = [permissions.IsAuthenticated, HasActiveSMSPanel]

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_queryset(self):
        return SMSTemplate.objects.filter(businessman=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SMSTemplateRetrieveAPIView(generics.RetrieveAPIView, mixins.UpdateModelMixin,
                                 mixins.DestroyModelMixin):

    serializer_class = SMSTemplateSerializer
    permission_classes = [permissions.IsAuthenticated, HasActiveSMSPanel]

    def get_queryset(self):
        return SMSTemplate.objects.filter(businessman=self.request.user)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

    def get_serializer_context(self):
        return {'user': self.request.user}





@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, HasActiveSMSPanel, HasValidCreditSendSMS])
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
        return send_message_failed_response(e)
    except HTTPException:
        return Response({'detail': 'خطا در ارسال پیام'}, status=status.HTTP_424_FAILED_DEPENDENCY)

    return create_sms_sent_success_response(request.user)





@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, HasActiveSMSPanel, HasValidCreditSendSMSToAll])
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
        return send_message_failed_response(e)
    except HTTPException:
        return Response({'detail': 'خطا در ارسال پیام'}, status=status.HTTP_424_FAILED_DEPENDENCY)

    return create_sms_sent_success_response(request.user)





@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, HasActiveSMSPanel, HasValidCreditSendSMS])
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
        return send_message_failed_response(e)
    except HTTPException as e:
        return Response({'detail': 'خطا درپردازش اطلاعات'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    return create_sms_sent_success_response(request.user)





@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, HasActiveSMSPanel, HasValidCreditSendSMSToAll])
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
        return send_message_failed_response(e)

    return create_sms_sent_success_response(request.user)



@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, HasActiveSMSPanel, HasValidCreditSendSMSToGroup])
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
        return send_message_failed_response(e)

    return create_sms_sent_success_response(request.user)





@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, HasActiveSMSPanel, HasValidCreditSendSMSToGroup])
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
        return send_message_failed_response(e)
    return create_sms_sent_success_response(request.user)


class FailedSMSMessagesList(BaseListAPIView):

    serializer_class = SMSMessageListSerializer

    def get_queryset(self):
        return self.request.user.smsmessage_set.filter(status=SMSMessage.STATUS_FAILED)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, HasActiveSMSPanel, HasValidCreditResendFailedSMS])
def resend_failed_sms(request, sms_id):
    try:
        sms = request.user.smsmessage_set.get(id=sms_id, status=SMSMessage.STATUS_FAILED)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    SendSMSMessage().set_message_to_pending(request.user, sms)
    serializer = SMSMessageListSerializer(sms)
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(['GET'])
def list_unsent_template_sms(request: Request):

    unsent_sms = request.user.unsenttemplatesms_set.order_by('-create_date').all()

    paginate = custom_paginator.NumberedPaginator(request, unsent_sms, UnsentTemplateSMSListSerializer)

    return paginate.next_page()





@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated, HasActiveSMSPanel, HasValidCreditResendFailedSMS])
def resend_plain_sms(request: Request, unsent_sms_id):

    try:
        unsent_plain_sms = request.user.unsentplainsms_set.get(id=unsent_sms_id)
    except ObjectDoesNotExist:
        return Response({'detail': 'unsent sms with provided id does not exist'}, status=status.HTTP_404_NOT_FOUND)

    messainger = SendSMSMessage()

    try:
        messainger.set_message_to_pending(request.user, unsent_plain_sms)
    except APIException as e:
        return send_message_failed_response(e)

    return create_sms_sent_success_response(request.user)






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
        return send_message_failed_response(e)

    return create_sms_sent_success_response(request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, HasActiveSMSPanel])
def get_businessman_sent_sms(request: Request):

    retrieve_link = create_link(reverse('sent_sms_retrieve'), request)
    page_num = get_query_param_or_default(request, 'page', 1)
    phone = get_query_param_or_default(request, 'phone')
    result = SentSMS.get_sent_sms_from_kavenegar(request.user, page_num, phone)
    return create_pagination_response_body(result[4], result[1], result[0], result[2], result[3], retrieve_link)


class RetrieveUpdateWelcomeMessageApiView(APIView):

    """
    Retrieves and updates data of the panel setting
    """

    def get(self, request: Request):

        """
        Represent current settings of the panel of the authenticated user
        :param request: Contains data of the request
        :return: Response with body of the current settings and 200 status code
        """
        wm = sms_message_service.get_welcome_message_or_create(request.user)
        sr = WelcomeMessageSerializer(wm)
        return ok(sr.data)

    def put(self, request: Request):

        """
        Updates Setting of the panel
        :param request: Contains data of the request
        :return: If new data for settings is invalid Returns Response with error messages and 400 status code, Else
        Response with body of the new settings and 200 status code
        """

        sr = WelcomeMessageSerializer(data=request.data, request=self.request)
        if not sr.is_valid():
            return bad_request(sr.errors)
        message = sr.validated_data.get('message')
        send_message = sr.validated_data.get('send_message')
        wm = sms_message_service.update_welcome_message(request.user, message, send_message)
        sr = WelcomeMessageSerializer(wm)
        return ok(sr.data)

