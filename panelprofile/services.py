from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from base_app.error_codes import ApplicationErrorCodes
from common.util.kavenegar_local import APIException
from common.util.sms_panel.client import ClientManagement, sms_client_management
from common.util.sms_panel.message import system_sms_message
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
            sms_panel.status = SMSPanelInfo.STATUS_ACTIVE
            sms_panel.save()
            return sms_panel
        except APIException as ex:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.KAVENEGAR_CLIENT_MANAGEMENT_ERROR, ex)

    def deactivate_sms_panel(self, user: Businessman) -> SMSPanelInfo:
        sms_panel = self.get_buinessman_sms_panel(user)
        try:
            sms_client_management.deactivate_sms_panel(sms_panel.api_key)
            sms_panel.status = SMSPanelInfo.STATUS_INACTIVE
            sms_panel.save()
            return sms_panel
        except APIException as ex:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.KAVENEGAR_CLIENT_MANAGEMENT_ERROR, ex)

    def has_sms_panel(self, user: Businessman) -> bool:
        return SMSPanelInfo.objects.filter(businessman=user).exists()

    def fetch_sms_panel_info(self, user: Businessman) -> SMSPanelInfo:
        sms_panel = self.get_buinessman_sms_panel(user)
        info = sms_client_management.fetch_user_by_api_key(sms_panel.api_key)
        sms_panel.api_key = info.api_key
        sms_panel.credit = info.credit
        sms_panel.sms_farsi_cost = info.sms_farsi_cost
        sms_panel.sms_english_cost = info.sms_english_cost
        sms_panel.status = info.status
        sms_panel.save()

        return sms_panel

    def create_sms_panel(self, user: Businessman, password: str) -> SMSPanelInfo:
        from users.services import businessman_service
        is_correct = businessman_service.is_password_correct(user, password)
        if not is_correct:
            raise ApplicationErrorCodes.get_exception(ApplicationErrorCodes.INVALID_PASSWORD)
        info = sms_client_management.add_user(user, password)
        info.businessman = user
        info.save()
        return info


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

    def businessman_auth_docs_upload(self,
                                     user: Businessman,
                                     form,
                                     national_card,
                                     birth_certificate,
                                     password) -> BusinessmanAuthDocs:

        from users.services import businessman_service

        with transaction.atomic():
            has_panel = sms_panel_info_service.has_sms_panel(user)
            if has_panel:
                sms_panel_info_service.fetch_sms_panel_info(user)
            else:
                sms_panel_info_service.create_sms_panel(user, password)

            doc = BusinessmanAuthDocs.objects.create(
                businessman=user, form=form,
                national_card=national_card,
                birth_certificate=birth_certificate
            )
            businessman_service.authdocs_uploaded_and_pending(user)

        try:
            system_sms_message.send_admin_authroize_docs_uploaded(user.username)
        except APIException as ex:
            pass

        return doc


sms_panel_info_service = SMSPanelInfoService()
business_man_auth_doc_service = BusinessmanAuthDocsService()
