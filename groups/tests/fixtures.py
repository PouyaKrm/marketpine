from base_app.tests import *
from groups.models import BusinessmanGroups, Membership


@pytest.fixture
def group_1(businessman_1_with_customer_tuple) -> BusinessmanGroups:
    g = BusinessmanGroups.objects.create(businessman=businessman_1_with_customer_tuple[0], title='fake group')

    for c in businessman_1_with_customer_tuple[1]:
        Membership.objects.create(group=g, customer=c)

    return g


@pytest.fixture
def group_1_customer_tuple(group_1) -> Tuple[BusinessmanGroups, List[Customer]]:
    customers = []
    for c in group_1.customers.all():
        customers.append(c)

    return group_1, customers
