from customer_application.error_codes import CustomerAppErrors
from customer_application.exceptions import CustomerServiceException
from customer_application.services import customer_data_service
from customer_return_plan.invitation.services import invitation_service
from customer_return_plan.loyalty.services import LoyaltyService
from customer_return_plan.models import Discount
from customer_return_plan.services import discount_service
from customers.services import customer_service
from users.models import Businessman, BusinessmanCustomer, Customer


class InvitationInfo:
    def __init__(self):
        self.customer = None
        self.businessman = None
        self.friend_phone = None
        self.friend_full_name = None
        self.full_name = None


class ReturnPlanService:

    def add_friend_invitation(self, info: InvitationInfo):
        customer_data_service.check_user_joined_businessman(info.businessman,
                                                            info.customer
                                                            )
        self._check_invitation_is_active(info.businessman)
        self._check_friend_already_invited(info.businessman, info.friend_phone)
        if not info.customer.is_full_name_set() and info.full_name is None:
            raise CustomerServiceException(CustomerAppErrors.FULL_NAME_MUST_BE_SET)
        elif not info.customer.is_full_name_set() and info.full_name is not None:
            info.customer.full_name = info.full_name
            info.customer.save()
        c = customer_service.add_customer(info.businessman, info.friend_phone, info.friend_full_name, None,
                                          BusinessmanCustomer.JOINED_BY_INVITATION)
        inviter_discount = invitation_service.create_invitation(info.businessman, info.customer, c)
        return {'discount_type': inviter_discount.discount_type, 'discount_code': inviter_discount.discount_code,
                'flat_rate_off': inviter_discount.flat_rate_off, 'percent_off': inviter_discount.percent_off}

    def _check_friend_already_invited(self, businessman: Businessman, friend_phone: str) -> str:
        if businessman.customers.filter(phone=friend_phone).exists():
            raise CustomerServiceException(CustomerAppErrors.FRIEND_ALREADY_INVITED)
        return friend_phone

    def _check_invitation_is_active(self, businessman: Businessman):
        if not invitation_service.is_invitation_enabled(businessman):
            raise CustomerServiceException(CustomerAppErrors.error_dict(CustomerAppErrors.FRIEND_INVITATION_DISABLED))

    def create_loyalty_discount(self, customer: Customer, businessman_id: int, loyalty_discount_id: int) -> Discount:
        businessman = customer_data_service.get_businessman_of_customer_by_id(customer, businessman_id)
        setting = LoyaltyService.get_instance().get_discount_setting(businessman, loyalty_discount_id)
        return discount_service.create_loyalty_discount(setting, customer,
                                                        CustomerAppErrors.ALREADY_HAS_LOYALTY_DISCOUNT)


return_plan_service = ReturnPlanService()
