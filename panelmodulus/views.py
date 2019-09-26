from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.request import Request
from rest_framework.response import Response
from .serializers import BusinessmanModulusSerializer
from common.util import paginators


@api_view(['GET'])
def get_businessman_modulus(request: Request):

    data = request.user.businessmanmodulus_set.all()

    # serializer = BusinessmanModulusSerializer(data, many=True)
    # return Response(serializer.data, status=status.HTTP_200_OK)

    paginate=paginators.NumberedPaginator(request, data, BusinessmanModulusSerializer)
    return paginate.next_page()
