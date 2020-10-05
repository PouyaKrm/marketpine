from payment.models import PanelActivationPlans


class PaymentService:

    def get_all_plans(self):
        return PanelActivationPlans.objects.filter(is_available=True).all()


payment_service = PaymentService()
