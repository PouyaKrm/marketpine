from django.core.exceptions import ObjectDoesNotExist, ValidationError
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from common.util.http_helpers import ok, bad_request
from customer_return_plan.invitation.models import FriendInvitation
from .serializers import FriendInvitationCreationSerializer, FriendInvitationListSerializer, \
    InvitationBusinessmanListSerializer, InvitationRetrieveSerializer, FriendInvitationSettingsSerializer
from users.models import Businessman
from common.util.custom_validators import phone_validator
from common.util import paginators
# Create your views here.
from rest_framework import generics


#ToDo this view is jus for test purposes and must not be used in production
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
        payload = serializer.create(serializer.validated_data)
        return Response(payload, status=status.HTTP_200_OK)


class BusinessmanInvitationListAPIView(generics.ListAPIView):

    serializer_class = InvitationBusinessmanListSerializer

    def get_serializer_context(self):
        return {'user': self.request.user}

    def get_queryset(self):
        customer_id = self.request.query_params.get('id')
        query = FriendInvitation.objects.filter(businessman=self.request.user).order_by('-create_date')
        if customer_id:
            return query.filter(inviter__id=customer_id).all()
        return query.all()


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def friend_invitation_retrieve(request: Request, invitation_id):

    try:
        invitation = request.user.friendinvitation_set.get(id=invitation_id)
    except ObjectDoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    invitation.new = False

    invitation.save()

    serializer = InvitationRetrieveSerializer(invitation)
    return Response(serializer.data, status=status.HTTP_200_OK)


class FriendInvitationSettingAPIView(APIView):

    def get(self, request):

        serializer = FriendInvitationSettingsSerializer(request.user.friendinvitationsettings)
        return ok(serializer.data)

    def put(self, request):
        serializer = FriendInvitationSettingsSerializer(data=request.data)
        if not serializer.is_valid():
            return bad_request(serializer.errors)
        serializer.update(request.user.friendinvitationsettings, serializer.validated_data)
        return ok(serializer.data)
