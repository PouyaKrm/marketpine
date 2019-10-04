from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from invitation.models import FriendInvitation, FriendInvitationDiscount
from .serializers import FriendInvitationCreationSerializer, FriendInvitationListSerializer, InvitationBusinessmanListSerializer, InvitationRetrieveSerializer
from users.models import Businessman
from common.util.custom_validators import phone_validator
from common.util import paginators, generate_discount_code, DiscountType
from .permissions import HasInvitationAccess
from common.util.sms_message import SMSMessage
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

        friend_Invitation_list= FriendInvitation.objects.filter(businessman=businessman, invited_by=customer).all()

        paginator = paginators.NumberedPaginator(request,friend_Invitation_list, FriendInvitationListSerializer)
        return paginator.next_page()


    def post(self, request):

        serializer = FriendInvitationCreationSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


        invited = serializer.data['invited']
        inviter = serializer.data['inviter']

        try:
            businessman = Businessman.objects.get(username=serializer.data['username'])
        except ObjectDoesNotExist:
            return Response({'username': ['این نام کاربری وجود ندارد']}, status=status.HTTP_404_NOT_FOUND)

        try:
            customer = businessman.customers.get(phone=inviter)
        except ObjectDoesNotExist:
            return Response({'invited_by': ['مشتری با این شماره تلفن وجود ندارد']}, status=status.HTTP_404_NOT_FOUND)

        if businessman.customers.filter(phone=invited).exists():
            return Response({'invited': ['این مشتری قبلا معرفی شده']}, status=status.HTTP_403_FORBIDDEN)

        if inviter == invited:
            return Response(status=status.HTTP_403_FORBIDDEN)

        invited_discount = generate_discount_code(DiscountType.INVITATION)


        invited_customer = businessman.customers.create(phone=invited)

        obj = FriendInvitation.objects.create(businessman=businessman, invited=invited_customer,
                                              inviter=customer)

        inviter_discount = FriendInvitationDiscount.objects.create(friend_invitation=obj, customer=customer, role='IR',
                                                        discount_code=generate_discount_code(DiscountType.INVITATION))

        FriendInvitationDiscount.objects.create(friend_invitation=obj, customer=invited_customer, role='ID',
                                                discount_code=invited_discount)

        payload = {'id': obj.id, 'businessman': businessman.username, 'inviter': inviter, 'invited': invited,
                   'invitation_date': obj.invitation_date, 'inviter_discount_code': inviter_discount.discount_code}

        sms = SMSMessage()

        sms.send_friend_invitation_welcome_message(businessman.business_name, invited, invited_discount)

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

    serializer = InvitationRetrieveSerializer(invitation)
    return Response(serializer.data, status=status.HTTP_200_OK)
