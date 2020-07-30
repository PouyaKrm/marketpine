from rest_framework import serializers


def get_request_obj(*args, **kwargs):
    context = kwargs.get('context')
    request = kwargs.get('request')

    if context is not None and context['request'] is not None:
        return context['request']

    elif request is not None:
        return request


class BaseModelSerializerWithRequestObj(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        self.request = get_request_obj(*args, **kwargs)
        super().__init__(*args, **kwargs)


class BaseSerializerWithRequestObj(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        self.request = get_request_obj(*args, **kwargs)
        super().__init__(*args, **kwargs)
