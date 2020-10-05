from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response


def ok(data) -> Response:
    return Response(data, status=status.HTTP_200_OK)


def no_content() -> Response:
    return Response(status=status.HTTP_204_NO_CONTENT)


def bad_request(errors) -> Response:
    return Response(errors, status=status.HTTP_400_BAD_REQUEST)


def not_found(data=None) -> Response:
    if data is None:
        return Response(status=status.HTTP_404_NOT_FOUND)
    return Response(data, status=status.HTTP_404_NOT_FOUND)


def dependency_failed(data=None) -> Response:
    return Response(data, status=status.HTTP_424_FAILED_DEPENDENCY)


def forbidden(data: dict = None) -> Response:
    return Response(data=data, status=status.HTTP_403_FORBIDDEN)


def created(data=None) -> Response:
    return Response(data=data, status=status.HTTP_201_CREATED)


def get_query_param_or_default(request: Request, name: str, default=None):
    param = request.query_params.get(name)
    if param is None:
        return default
    return param


def get_user_agent(request: Request) -> str:
    return request.META.get('HTTP_USER_AGENT')
