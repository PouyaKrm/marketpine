from django.conf import settings
from rest_framework import generics, mixins, permissions, status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from base_app.error_codes import ApplicationErrorException
from base_app.views import BaseListAPIView
from common.util.http_helpers import ok, bad_request
from common.util.kavenegar_local import APIException
from panelprofile.serializers import SMSPanelInfoSerializer
from users.models import Businessman
from .models import SMSTemplate
from .permissions import HasValidCreditSendSMSToInviduals, HasValidCreditSendSMSToAll, HasValidCreditResendFailedSMS, \
    HasValidCreditSendSMSToGroup, HasActiveSMSPanel
from .serializers import SMSMessageListSerializer, WelcomeMessageSerializer, SentSMSSerializer
from .serializers import SMSTemplateSerializer, SendSMSSerializer, SendPlainSMSToAllSerializer, \
    SendByTemplateSerializer, SendPlainToGroup
from .services import sms_message_service

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

        try:
            info = sms_message_service.send_plain_sms(
                request.user,
                serializer.validated_data.get('customers'),
                serializer.validated_data.get('content')
            )
            sr = SMSPanelInfoSerializer(info)
            return ok(sr.data)
        except ApplicationErrorException as e:
            return bad_request(e.http_message)


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

        try:
            info = sms_message_service.send_plain_sms_to_all(
                request.user,
                serializer.validated_data.get('content')
            )
            sr = SMSPanelInfoSerializer(info)
            return ok(sr.data)
        except ApplicationErrorException as ex:
            return bad_request(ex.http_message)


class SendByTemplateAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated, HasActiveSMSPanel,
                          HasValidCreditSendSMSToInviduals]

    def post(self, request):
        serializer = SendByTemplateSerializer(data=request.data, context={'user': request.user})
        if not serializer.is_valid():
            return bad_request(serializer.errors)

        try:
            info = sms_message_service.send_by_template(
                request.user,
                serializer.validated_data.get('customers'),
                serializer.validated_data.get('template')
            )
            sr = SMSPanelInfoSerializer(info)
            return ok(sr.data)
        except ApplicationErrorException as ex:
            return bad_request(ex.http_message)


class SendByTemplateToAll(APIView):
    permission_classes = [permissions.IsAuthenticated, HasActiveSMSPanel,
                          HasValidCreditSendSMSToAll]

    def post(self, request: Request, template_id: int):
        try:
            info = sms_message_service.send_by_template_to_all(request.user, template_id)
            sr = SMSPanelInfoSerializer(info)
            return ok(sr.data)
        except ApplicationErrorException as ex:
            return bad_request(ex.http_message)


class SendPlainSmsToGroup(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        HasActiveSMSPanel,
        HasValidCreditSendSMSToGroup
    ]

    def post(self, request: Request, group_id):
        sr = SendPlainToGroup(data=request.data)
        if not sr.is_valid():
            return bad_request(sr.errors)

        try:
            info = sms_message_service.send_plain_to_group(request.user, group_id, sr.validated_data.get('content'))
            sr = SMSPanelInfoSerializer(info)
            return ok(sr.data)
        except ApplicationErrorException as ex:
            return bad_request(ex.http_message)


class SendTemplateSmsToGroup(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        HasActiveSMSPanel,
        HasValidCreditSendSMSToGroup
    ]

    def post(self, request: Request, template_id: int, group_id: int):
        try:
            info = sms_message_service.send_by_template_to_group(request.user, group_id, template_id)
            sr = SMSPanelInfoSerializer(info)
            return ok(sr.data)
        except ApplicationErrorException as ex:
            return bad_request(ex.http_message)


class FailedSMSMessagesList(BaseListAPIView):
    serializer_class = SMSMessageListSerializer

    def get_queryset(self):
        return sms_message_service.get_failed_messages(self.request.user)


class ResendFailedSms(APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        HasActiveSMSPanel,
        HasValidCreditResendFailedSMS
    ]

    def post(self, request: Request, sms_id: int):

        try:
            info = sms_message_service.resend_failed_message(request.user, sms_id)
            sr = SMSPanelInfoSerializer(info)
            return ok(sr.data)
        except ApplicationErrorException as ex:
            return bad_request(ex.http_message)


class SentSMSRetrieveAPIView(BaseListAPIView):
    permission_classes = [permissions.IsAuthenticated, HasActiveSMSPanel]
    serializer_class = SentSMSSerializer

    def get_queryset(self):
        phone = self.request.query_params.get('phone')
        return sms_message_service.get_sent_sms(self.request.user, phone)


class RetrieveUpdateWelcomeMessageApiView(APIView):
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
