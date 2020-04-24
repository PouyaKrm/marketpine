from rest_framework import status
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
