from rest_framework.decorators import api_view
from rest_framework.request import Request

from common.util.http_helpers import ok
from .festivals.models import Festival
from .invitation.models import FriendInvitation


@api_view(['GET'])
def dashboard_data(request: Request):

    festivals = Festival.objects.count()
    friend_invitations = FriendInvitation.objects.count()
    return ok({'festivals_total': festivals, 'invitations_total': friend_invitations})