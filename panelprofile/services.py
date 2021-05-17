from django.core.exceptions import ObjectDoesNotExist

from base_app.error_codes import ApplicationErrorCodes
from common.util.kavenegar_local import APIException
from common.util.sms_panel.client import ClientManagement, sms_client_management
from panelprofile.models import SMSPanelInfo, SMSPanelStatus, BusinessmanAuthDocs
from smspanel.models import SMSMessage
from users.models import Businessman


client = ClientManagement()

class SMSPanelInfoService:


    def increase_credit_in_tomans(self, sms_panel_info: SMSPanelInfo, amount_in_tomans: int) -> int:
        """
                a shortcut to increase amount of credit of businessman
                :param amount: amount on increase of businessman
                :raises ValueError If value is not positive or is smaller that 1000 this exception will be thrown
                :raises APIException If Transaction failed
                :return: if success in credit increasement returns (true, amount of new credit) else (false, -1)
                """

        amount = amount_in_tomans * 10
        if amount <= 0 or amount < 1000:
            raise ValueError("amount must be positive and bigger that 1000 Rials")
        new_credit = client.change_credit(amount, sms_panel_info.api_key, "افزایش اعتبار پنل اسمس")
        sms_panel_info.credit = new_credit
        sms_panel_info.save()
        return sms_panel_info.credit

    def decrease_credit_in_tomans(self, sms_panel_info: SMSPanelInfo, amount_in_tomans: int):

        amount_in_tomans = amount_in_tomans * 10
        if amount_in_tomans < 0 or amount_in_tomans > sms_panel_info.credit:
            raise ValueError('credit amount_in_tomans is invalid')
        new_credit = client.change_credit(-amount_in_tomans, sms_panel_info.api_key, 'کاهش اعتبار پنل پیامک')
        sms_panel_info.credit = new_credit
        sms_panel_info.save()

    def has_valid_credit_to_send_to_all(self, user: Businessman) -> bool:
        return user.has_sms_panel and user.smspanelinfo.has_valid_credit_to_send_message_to_all()

    def get_buinessman_sms_panel(self, user: Businessman) -> SMSPanelInfo:

        try:
            return SMSPanelInfo.objects.get(businessman=user)
        except ObjectDoesNotExist:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.BUSINESSMAN_HAS_NO_SMS_PANEL)

    def activate_sms_panel(self, user: Businessman) -> SMSPanelInfo:
        sms_panel = self.get_buinessman_sms_panel(user)

        try:
            sms_client_management.activate_sms_panel(sms_panel.api_key)
            sms_panel.status = SMSPanelStatus.ACTIVE_LOGIN
            sms_panel.save()
            return sms_panel
        except APIException as ex:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.KAVENEGAR_CLIENT_MANAGEMENT_ERROR, ex)

    def deactivate_sms_panel(self, user: Businessman) -> SMSPanelInfo:
        sms_panel = self.get_buinessman_sms_panel(user)
        try:
            sms_client_management.deactivate_sms_panel(sms_panel.api_key)
            sms_panel.status = SMSPanelStatus.INACTIVE
            sms_panel.save()
            return sms_panel
        except APIException as ex:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.KAVENEGAR_CLIENT_MANAGEMENT_ERROR, ex)


class BusinessmanAuthDocsService:

    def delete_businessman_docs(self, user: Businessman) -> BusinessmanAuthDocs:
        doc = self._get_businessman_auth_docs(user)
        doc.delete()
        return doc

    def _get_businessman_auth_docs(self, user: Businessman):

        try:
            return BusinessmanAuthDocs.objects.get(businessman=user)
        except ObjectDoesNotExist as ex:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.BUSINESSMAN_HAS_NO_AUTH_DOCS, ex)


sms_panel_info_service = SMSPanelInfoService()
business_man_auth_doc_service = BusinessmanAuthDocsService()