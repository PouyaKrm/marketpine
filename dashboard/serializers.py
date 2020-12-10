from datetime import timedelta

from rest_framework import serializers

from base_app.serializers import BaseSerializerWithRequestObj, BaseModelSerializerWithRequestObj
from customer_return_plan.invitation.services import invitation_service
from customer_return_plan.services import discount_service
from customerpurchase.services import purchase_service
from customers.services import customer_service
from users.models import Businessman
import jdatetime


class DashboardSerializer(BaseModelSerializerWithRequestObj):

    def __init__(self, *args, **kwargs):

        self.days_record = []
        self.output_dict = []
        now = jdatetime.datetime.now()
        p_d = jdatetime.datetime(now.year, now.month, 1)
        self.start_date = p_d.togregorian()
        self.end_date = now.togregorian()
        for i in range(now.day):
            self.days_record.append(p_d.togregorian())

            self.output_dict.append({
                'persian_date': p_d.date().strftime("%Y/%m/%d"),
                'persian_weekday': p_d.weekday(),
                'gregorian_date': p_d.togregorian().strftime('%Y-%m-%d')
            })
            p_d = p_d + jdatetime.timedelta(days=1)

        super().__init__(*args, **kwargs)

    customers_total = serializers.SerializerMethodField(read_only=True)
    invitations_total = serializers.SerializerMethodField(read_only=True)
    used_discounts_total = serializers.SerializerMethodField(read_only=True)
    bar_chart_data = serializers.SerializerMethodField(read_only=True)
    pi_chart_data = serializers.SerializerMethodField(read_only=True)
    linear_charts_data = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Businessman
        fields = [
            'customers_total',
            'invitations_total',
            'used_discounts_total',
            'bar_chart_data',
            'pi_chart_data',
            'linear_charts_data',
        ]

    def get_customers_total(self, obj):

        return customer_service.get_businessman_customers(self.request.user).count()

    def get_invitations_total(self, obj):

        return invitation_service.get_businessman_all_invitations(self.request.user).count()

    def get_used_discounts_total(self, obj):
        return purchase_service.get_all_businessman_purchases_by_dsicount(self.request.user).count()

    def get_bar_chart_data(self, obj):
        festival_count = discount_service.get_used_festival_discounts_in_month(obj, self.start_date).count()
        invitation_count = discount_service.get_used_invitation_discounts_in_month(obj, self.start_date).count()
        return {
            'used_festival_discounts_total': festival_count,
            'used_invitation_discounts_total': invitation_count
        }

    def get_linear_charts_data(self, obj):
        customers_in_month = []
        invitations_in_month = []
        for i in self.days_record:
            count = customer_service.customer_registered_in_date(obj, i).count()
            customers_in_month.append(count)
            count2 = invitation_service.invitations_added_in_month(obj, i).count()
            invitations_in_month.append(count2)
        return {
            'time_range': self.output_dict,
            'customers_added': customers_in_month,
            'invitations_added': invitations_in_month
        }

    def get_pi_chart_data(self, obj):

        from groups.models import BusinessmanGroups
        g = BusinessmanGroups.get_purchase_top_group_or_create(obj)
        result = []
        for i in g.customers.all():
            p_sum = purchase_service.get_customer_purchase_sum(obj, i)
            result.append({
                'phone': i.phone,
                'full_name': i.full_name,
                'purchase_sum': p_sum
            })
        return result



