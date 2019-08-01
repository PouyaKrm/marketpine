from django.template import Template
from django.template.context import Context
from festivals.models import Festival
from users.models import Businessman, Customer
from . import jalali

def get_template_context(customer: Customer):

    return {'phone': customer.phone, 'telegram_id': customer.telegram_id,
               'instagram_id': customer.instagram_id, 'business_name': customer.businessman.business_name}


def get_fake_context(user: Businessman):

    return {'phone': '09582562418', 'telegram_id': '@mohammad12', 'business_name': user.business_name, 'instagram_id': '@insta_test'}


def render_template(template: str, context: dict):
    """
        reference: https://docs.djangoproject.com/en/2.2/ref/templates/api/#rendering-a-context
    """
    template = Template(template)
    context = Context(context)
    return template.render(context)


def render_template_with_customer_data(template: str, customer: Customer):

    return render_template(template, get_template_context(customer))


class FestivalTemplate:

    """
    contains data and functions that is needed to render  a template message for specific festival
    """

    def __init__(self, businessman: Businessman, festival: Festival):

        self.businessman = businessman
        self.festival = festival

    @staticmethod
    def get_fake_context():

        """
        Provides a Fake context that for validating templates
        :return: ContextObject
        """

        return Context({'business_name': 'test', 'festival_name': 'test', 'discount_code': 'test',
                 'percent_off': 'test', 'flat_rate_off': 'test', 'start_date': 'test', 'end_date': 'test'})

    @staticmethod
    def validate_template(template: str):

        Template(template).render(FestivalTemplate.get_fake_context())

    def get_context(self):

        """
        Provides the context that is needed to render templates that are related to festivals
        :return: ContextObject
        """

        return Context({'business_name': self.businessman.business_name, 'festival_name': self.festival.name,
                           'discount_code': self.festival.discount_code,
                           'percent_off': self.festival.percent_off, 'flat_rate_off': self.festival.flat_rate_off,
                           'start_date': jalali.Gregorian(self.festival.start_date.__str__()).persian_string("{}/{}/{}"),
                           'end_date': jalali.Gregorian(self.festival.end_date.__str__()).persian_string("{}/{}/{}")})




    def get_message_phone_lists(self):

        """
        Renders template for each customer of a businessman
        :return: List of rendered messages and List of phone numbers of each customer as dictionary
        """

        message_list = []
        phone_list = []

        template = Template(self.festival.message)

        context = self.get_context()

        for c in self.businessman.customers.all():

            context['phone'] = c.phone

            message_list.append(template.render(context))
            phone_list.append(c.phone)

        return {'messages': message_list, 'phones': phone_list}



