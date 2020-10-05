from rest_framework.request import Request

from payment.models import PanelActivationPlans, Payment, PaymentTypes
from users.models import Businessman


class PaymentService:

    def get_all_plans(self):
        return PanelActivationPlans.objects.filter(is_available=True).order_by('duration').all()

    def plan_exist_by_id(self, plan_id: int) -> bool:
        return PanelActivationPlans.objects.filter(id=plan_id).exists()

    def get_plan_by_id(self, plan_id) -> PanelActivationPlans:
        return PanelActivationPlans.objects.get(id=plan_id)

    def create_panel_activation_payment(self, request: Request, plan: PanelActivationPlans, description: str) -> Payment:
        p = Payment.objects.create(businessman=request.user, payment_type=PaymentTypes.ACTIVATION,
                                   amount=plan.price_in_toman, phone=request.user.phone,
                                   description=description, panel_plan=plan)
        p.pay(request)
        return p


payment_service = PaymentService()
