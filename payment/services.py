from django.conf import settings
from django.urls import reverse
from rest_framework.request import Request
from zeep import Client

from base_app.error_codes import ApplicationErrorException, ApplicationErrorCodes
from payment.models import PanelActivationPlans, Payment, PaymentTypes
from users.models import Businessman

url = settings.ZARINPAL.get('url')
setting_merchant = settings.ZARINPAL.get('MERCHANT')


class PaymentService:

    def get_all_plans(self):
        return PanelActivationPlans.objects.filter(is_available=True).order_by('duration').all()

    def plan_exist_by_id(self, plan_id: int) -> bool:
        return PanelActivationPlans.objects.filter(id=plan_id).exists()

    def get_plan_by_id(self, plan_id) -> PanelActivationPlans:
        return PanelActivationPlans.objects.get(id=plan_id)

    def create_panel_activation_payment(self, request: Request, plan: PanelActivationPlans,
                                        description: str) -> Payment:
        p = Payment.objects.create(businessman=request.user, payment_type=PaymentTypes.ACTIVATION,
                                   amount=plan.price_in_toman, phone=request.user.phone,
                                   description=description, panel_plan=plan)
        p.pay(request)
        return p

    def create_payment_for_smspanel_credit(self,
                                           request: Request,
                                           user: Businessman,
                                           amount_tomal: float,
                                           ):

        return self._create_payment(request, user, amount_tomal, 'افزایش اعتبار پنل اسمس', Payment.TYPE_SMS)

    def _create_payment(self, request: Request, user: Businessman, amount_toman: float, description: str,
                        payment_type) -> Payment:
        try:
            p = Payment.objects.create(
                businessman=user,
                amount=amount_toman,
                description=description,
                phone=user.phone,
                payment_type=payment_type
            )
            call_back = request.build_absolute_uri(reverse('payment:verify'), )
            client = Client(url)
            merchant = setting_merchant
            result = client.service.PaymentRequest(merchant, p.amount, p.description, p.businessman.email,
                                                   p.phone, call_back)
            p.create_status = result.Status
            p.save()
            if p.create_status == 100:
                p.authority = result.Authority
                p.save()
            else:
                raise ApplicationErrorException(ApplicationErrorCodes.PAYMENT_CREATION_FAILED)

            return p

        except Exception as ex:
            raise ApplicationErrorException(ApplicationErrorCodes.PAYMENT_CREATION_FAILED, ex)


payment_service = PaymentService()
