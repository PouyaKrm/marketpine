from datetime import timedelta

from rest_framework import serializers

from base_app.serializers import BaseSerializerWithRequestObj, BaseModelSerializerWithRequestObj
from customer_return_plan.invitation.services import invitation_service
from customerpurchase.services import purchase_service
from customers.services import customer_service
from users.models import Businessman
import jdatetime


class DashboardSerializer(BaseModelSerializerWithRequestObj):

    def __init__(self, *args, **kwargs):
        now = jdatetime.datetime.now()
        print(jdatetime.datetime.now().togregorian())
        self.days_record = []
        self.output_dict = []
        p_d = jdatetime.datetime(now.year, now.month, 1)
        for i in range(now.day):
            self.days_record.append(p_d.togregorian())

            self.output_dict.append({
                'persian_date': p_d.date().strftime("%Y/%m/%d"),
                'persian_weekday': p_d.weekday(),
                'gregorian_date': p_d.togregorian().strftime('%Y-%m-%d')
            })
            p_d = p_d + jdatetime.timedelta(days=1)

        print(self.days_record)

        super().__init__(*args, **kwargs)

    customers_total = serializers.SerializerMethodField(read_only=True)
    invitations_total = serializers.SerializerMethodField(read_only=True)
    used_discounts_total = serializers.SerializerMethodField(read_only=True)
    dates_range = serializers.SerializerMethodField(read_only=True)
    customers_added_in_days_of_month = serializers.SerializerMethodField(read_only=True)
    invitations_added_in_month = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Businessman
        fields = [
            'customers_total',
            'invitations_total',
            'used_discounts_total',
            'dates_range',
            'customers_added_in_days_of_month',
            'invitations_added_in_month',
        ]

    def get_customers_total(self, obj):

        return customer_service.get_businessman_customers(self.request.user).count()

    def get_invitations_total(self, obj):

        return invitation_service.get_businessman_all_invitations(self.request.user).count()

    def get_used_discounts_total(self, obj):
        return purchase_service.get_all_businessman_purchases_by_dsicount(self.request.user).count()

    def get_dates_range(self, obj):
        return self.output_dict

    def get_customers_added_in_days_of_month(self, obj):
        result = []
        for i in self.days_record:
            count = customer_service.customer_registered_in_date(obj, i).count()
            result.append(count)
        return result

    def get_invitations_added_in_month(self, obj):
        result = []
        for i in self.days_record:
            count = invitation_service.invitations_added_in_month(obj, i).count()
            result.append(count)
        return result

