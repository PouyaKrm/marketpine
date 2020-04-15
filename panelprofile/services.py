from common.util.sms_panel.client import ClientManagement
from panelprofile.models import SMSPanelInfo
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

    def set_wait_for_charge_to_pending(self):
        SMSMessage.objects.filter(status=SMSMessage.STATUS_WAIT_FOR_CREDIT_RECHARGE).update(
            status=SMSMessage.STATUS_PENDING)


sms_panel_info_service = SMSPanelInfoService()
