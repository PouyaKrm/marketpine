import logging

from django.conf import settings
from django.http.response import HttpResponse
from django.views.generic.base import View
from rest_framework import permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from base_app.views import BaseListAPIView
from common.util.http_helpers import ok, bad_request
from common.util.kavenegar_local import APIException
from panelprofile.serializers import SMSPanelInfoSerializer
from users.models import Businessman
from .permissions import HasValidCreditSendSMSToInviduals, HasValidCreditSendSMSToAll, HasValidCreditResendFailedSMS, \
    HasValidCreditSendSMSToGroup, HasActiveSMSPanel
from .selectors import get_sms_templates, get_sms_template_by_id, get_failed_messages, get_sent_sms, get_welcome_message
from .serializers import SMSMessageListSerializer, WelcomeMessageSerializer, SentSMSSerializer
from .serializers import SMSTemplateSerializer, SendSMSSerializer, SendPlainSMSToAllSerializer, \
    SendByTemplateSerializer, SendPlainToGroup
from .services import create_sms_template, update_sms_template, delete_sms_template, \
    send_plain_sms, send_plain_sms_to_all, send_by_template, send_by_template_to_all, send_plain_to_group, \
    send_by_template_to_group, resend_failed_message, update_welcome_message, update_sent_sms_status

page_size = settings.PAGINATION_PAGE_NUM

logger = logging.getLogger('django')


def create_sms_sent_success_response(user: Businessman):
    return Response({'credit': user.smspanelinfo.credit}, status=status.HTTP_200_OK)


def send_message_failed_response(ex: APIException):
    return Response({'status': ex.status, 'message': ex.message}, status=status.HTTP_424_FAILED_DEPENDENCY)


class SMSTemplateList(APIView):
    permission_classes = [permissions.IsAuthenticated, HasActiveSMSPanel]

    def get(self, request: Request):
        templates = get_sms_templates(businessman=request.user)
        sr = SMSTemplateSerializer(templates, many=True)
        return ok(sr.data)

    def post(self, request: Request):
        sr = SMSTemplateSerializer(data=request.data, context={'user': request.user})
        if not sr.is_valid():
            return bad_request(sr.errors)

        template = create_sms_template(businessman=request.user,
                                       title=sr.validated_data.get('title'),
                                       content=sr.validated_data.get('content')
                                       )
        sr = SMSTemplateSerializer(template, context={'user': request.user})
        return ok(sr.data)


class SMSTemplateRetrieveAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasActiveSMSPanel]

    def get(self, request: Request, template_id: int):
        t = get_sms_template_by_id(businessman=request.user, template_id=template_id)
        sr = SMSTemplateSerializer(t, context={'user': request.user})
        return ok(sr.data)

    def put(self, request: Request, template_id: int):
        sr = SMSTemplateSerializer(data=request.data, context={'user': request.user})
        if not sr.is_valid():
            return bad_request(sr.errors)
        t = update_sms_template(businessman=request.user,
                                template_id=template_id,
                                title=sr.validated_data.get('title'),
                                content=sr.validated_data.get('content')
                                )
        sr = SMSTemplateSerializer(t, context={'user': request.user})
        return ok(sr.data)

    def delete(self, request, template_id: int):
        t = delete_sms_template(businessman=request.user, template_id=template_id)
        sr = SMSTemplateSerializer(t, context={'user': request.user})
        return ok(sr.data)


class SendPlainSms(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        HasActiveSMSPanel,
        HasValidCreditSendSMSToInviduals
    ]

    """
    sends sms message without using template.
    :param request: contains message content and id of customers that are receptors of message
    :return: If data is invalid, Response with status code 400, else if error
    was occurred in kavenegar api, returns Response with a message from SMS API with error message
    other that 400.  With status code 500 if other error occurred.
     If operation was successful, Response with status code 204
    """

    def post(self, request: Request):
        serializer = SendSMSSerializer(data=request.data, context={'user': request.user})

        if not serializer.is_valid():
            return bad_request(serializer.errors)

        info = send_plain_sms(
            businessman=request.user,
            customer_ids=serializer.validated_data.get('customers'),
            message=serializer.validated_data.get('content')
        )
        sr = SMSPanelInfoSerializer(info)
        return ok(sr.data)


class SendPlainToAllAPIView(APIView):
    """
    sends a same message to all customers of a businessman.
    :return: If data is invalid, Response with status code 400, else if error
    was occurred in kavenegar api, returns Response with a message from SMS API with error message
    other that 400.  With status code 424 if other error occurred.
     If operation was successful, Response with status code 204
    """

    permission_classes = [permissions.IsAuthenticated, HasActiveSMSPanel,
                          HasValidCreditSendSMSToAll]

    def post(self, request: Request):
        serializer = SendPlainSMSToAllSerializer(data=request.data, context={'user': request.user})

        if not serializer.is_valid():
            return bad_request(serializer.errors)

        info = send_plain_sms_to_all(
            businessman=request.user,
            message=serializer.validated_data.get('content')
        )
        sr = SMSPanelInfoSerializer(info)
        return ok(sr.data)


class SendByTemplateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasActiveSMSPanel,
                          HasValidCreditSendSMSToInviduals]

    def post(self, request):
        serializer = SendByTemplateSerializer(data=request.data, context={'user': request.user})
        if not serializer.is_valid():
            return bad_request(serializer.errors)

        info = send_by_template(
            businessman=request.user,
            customer_ids=serializer.validated_data.get('customers'),
            template=serializer.validated_data.get('template')
        )
        sr = SMSPanelInfoSerializer(info)
        return ok(sr.data)


class SendByTemplateToAll(APIView):
    permission_classes = [permissions.IsAuthenticated, HasActiveSMSPanel,
                          HasValidCreditSendSMSToAll]

    def post(self, request: Request, template_id: int):
        info = send_by_template_to_all(businessman=request.user, template=template_id)
        sr = SMSPanelInfoSerializer(info)
        return ok(sr.data)


class SendPlainSmsToGroupAPIView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        HasActiveSMSPanel,
        HasValidCreditSendSMSToGroup
    ]

    def post(self, request: Request, group_id):
        sr = SendPlainToGroup(data=request.data)
        if not sr.is_valid():
            return bad_request(sr.errors)

        info = send_plain_to_group(businessman=request.user, group_id=group_id,
                                   message=sr.validated_data.get('content'))
        sr = SMSPanelInfoSerializer(info)
        return ok(sr.data)


class SendTemplateSmsToGroupAPIView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        HasActiveSMSPanel,
        HasValidCreditSendSMSToGroup
    ]

    def post(self, request: Request, template_id: int, group_id: int):
        info = send_by_template_to_group(businessman=request.user, group_id=group_id, template_id=template_id)
        sr = SMSPanelInfoSerializer(info)
        return ok(sr.data)


class FailedSMSMessagesList(BaseListAPIView):
    serializer_class = SMSMessageListSerializer

    def get_queryset(self):
        return get_failed_messages(businessman=self.request.user)


class ResendFailedSmsAPIView(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        HasActiveSMSPanel,
        HasValidCreditResendFailedSMS
    ]

    def post(self, request: Request, sms_id: int):
        info = resend_failed_message(businessman=request.user, sms_id=sms_id)
        sr = SMSPanelInfoSerializer(info)
        return ok(sr.data)


class SentSMSListAPIView(BaseListAPIView):
    permission_classes = [permissions.IsAuthenticated, HasActiveSMSPanel]
    serializer_class = SentSMSSerializer

    def get_queryset(self):
        phone = self.request.query_params.get('phone')
        return get_sent_sms(businessman=self.request.user, receptor_phone=phone)


class RetrieveUpdateWelcomeMessageAPIView(APIView):
    """
    Retrieves and updates data of the panel setting
    """

    permissions = [permissions.IsAuthenticated, HasActiveSMSPanel]

    def get(self, request: Request):
        """
        Represent current settings of the panel of the authenticated user
        :param request: Contains data of the request
        :return: Response with body of the current settings and 200 status code
        """
        wm = get_welcome_message(businessman=request.user)
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
        wm = update_welcome_message(businessman=request.user, message=message, send_message=send_message)
        sr = WelcomeMessageSerializer(wm)
        return ok(sr.data)


class DeliveryCallbackView(View):

    def post(self, request):
        messageid = request.POST.get('messageid')
        try:
            new_status = int(request.POST.get('status'))
            update_sent_sms_status(messageid=messageid, status=new_status)
        except ValueError as ex:
            logger.error(ex)
            return HttpResponse(content='ok', status=200)
        return HttpResponse(content='ok', status=200)
