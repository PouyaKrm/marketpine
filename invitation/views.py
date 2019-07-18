from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from invitation.models import FriendInvitation
from .serializers import FriendInvitationCreationSerializer, FriendInvitationListSerializer, InvitationBusinessmanListSerializer, InvitationBusinessmanRetrieveSerializer
from users.models import Businessman
from common.util.custom_validators import phone_validator
from common.util import paginators
from .permissions import HasInvitationAccess
# Create your views here.


class FriendInvitationListAPIView(APIView):

    def get(self, request: Request):

        phone = request.query_params.get('phone')
        username = request.query_params.get('username')

        if (phone is None) or (username is None):
            return Response({'details': ['phone number and username is required']}, status=status.HTTP_400_BAD_REQUEST)

        try:
            phone_validator(phone)
        except ValidationError as e:
            return Response({'details': e}, status=status.HTTP_400_BAD_REQUEST)

        try:
            businessman = Businessman.objects.get(username=username)
        except ObjectDoesNotExist:
            return Response({'username': ['این نام کاربری وجود ندارد']}, status=status.HTTP_404_NOT_FOUND)

        try:
            customer = businessman.customers.get(phone=phone)
        except ObjectDoesNotExist:
            return Response({'invited_by': ['مشتری با این شماره تلفن وجود ندارد']}, status=status.HTTP_404_NOT_FOUND)

        paginator = paginators.NumberedPaginator(request, FriendInvitation.objects.
                                                 filter(businessman=businessman, invited_by=customer).all(), FriendInvitationListSerializer)

        return paginator.next_page()


    def post(self, request):

        serializer = FriendInvitationCreationSerializer(data=request.data)


        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        friend_phone = serializer.data['friend_phone']

        try:
            businessman = Businessman.objects.get(username=serializer.data['username'])
        except ObjectDoesNotExist:
            return Response({'username': ['این نام کاربری وجود ندارد']}, status=status.HTTP_404_NOT_FOUND)

        try:
            customer = businessman.customers.get(phone=serializer.data['invited_by'])
        except ObjectDoesNotExist:
            return Response({'invited_by': ['مشتری با این شماره تلفن وجود ندارد']}, status=status.HTTP_404_NOT_FOUND)

        if businessman.friendinvitation_set.filter(friend_phone=friend_phone).exists():
            return Response({'friend_phone': ['این مشتری قبلا معرفی شده']}, status=status.HTTP_403_FORBIDDEN)

        if customer.phone == friend_phone:
            return Response(status=status.HTTP_403_FORBIDDEN)

        obj = FriendInvitation.objects.create(businessman=businessman, invited_by=customer,
                                              friend_phone=friend_phone)

        payload = {'id': obj.id, 'username': businessman.username, 'invited_by': customer.phone,
                              'friend_phone': obj.friend_phone, 'invitation_date': obj.invitation_date}

        return Response(payload, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, HasInvitationAccess])
def list_friend_invitation_businessman(request: Request):

    invitations = request.user.friendinvitation_set.all()

    paginator = paginators.NumberedPaginator(request, invitations, InvitationBusinessmanListSerializer)

    return paginator.next_page()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated, HasInvitationAccess])
def friend_invitation_retrieve(request: Request, invitation_id):

    try:
        invitation = request.user.friendinvitation_set.get(id=invitation_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    invitation.new = False

    invitation.save()

    serializer = InvitationBusinessmanRetrieveSerializer(invitation)
    return Response(serializer.data, status=status.HTTP_200_OK)
