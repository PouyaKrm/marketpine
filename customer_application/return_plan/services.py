from customer_application.error_codes import CustomerAppErrors
from customer_application.exceptions import CustomerServiceException
from customer_return_plan.invitation.models import FriendInvitationSettings
from customer_return_plan.invitation.services import invitation_service
from customer_return_plan.models import Discount
from customer_return_plan.services import discount_service
from customers.services import customer_service
from users.models import Businessman, Customer


class ReturnPlanService:

    def add_friend_invitation(self, customer: Customer, businessman: Businessman, friend_phone: str):
        self._check_invitation_is_active(businessman)
        self._check_friend_already_invited(businessman, friend_phone)
        c = customer_service.add_customer(businessman, friend_phone)
        inviter_discount = invitation_service.create_invitation(businessman, customer, c)
        return {'discount_type': inviter_discount.discount_type, 'discount_code': inviter_discount.discount_code,
                'flat_rate_off': inviter_discount.flat_rate_off, 'percent_off': inviter_discount.percent_off}

    def _check_friend_already_invited(self, businessman: Businessman, friend_phone: str) -> str:
        if businessman.customers.filter(phone=friend_phone).exists():
            CustomerServiceException.for_friend_already_invited()
        return friend_phone

    def _check_invitation_is_active(self, businessman: Businessman):
        if not invitation_service.is_invitation_enabled(businessman):
            raise CustomerServiceException(CustomerAppErrors.error_dict(CustomerAppErrors.FRIEND_INVITATION_DISABLED))


return_plan_service = ReturnPlanService()
