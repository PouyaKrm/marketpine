from rest_framework import serializers

from common.util import create_link


def get_request_obj(*args, **kwargs):
    context = kwargs.get('context')

    if context is not None and context.get('request') is not None:
        return context['request']

    elif kwargs.keys().__contains__('request'):
        return kwargs.get('request')


def pop_request_if_exist(**kwargs):
    kw = kwargs.copy()
    if kw.keys().__contains__('request'):
        kw.pop('request')
    return kw

def add_request_to_context_if_exist(request, **kwargs):
    kw = kwargs.copy()
    context = kw.get('context')
    if context is None:
        context = {}
    if context.get('request') is None:
        context['request'] = request
    kw['context'] = context
    return kw


class BaseModelSerializerWithRequestObj(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        self.request = get_request_obj(*args, **kwargs)
        kw = pop_request_if_exist(**kwargs)
        kw = add_request_to_context_if_exist(self.request, **kw)
        super().__init__(*args, **kw)


class BaseSerializerWithRequestObj(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        self.request = get_request_obj(*args, **kwargs)
        kw = pop_request_if_exist(**kwargs)
        kw = add_request_to_context_if_exist(self.request, **kw)
        super().__init__(*args, **kw)


class FileFieldWithLinkRepresentation(serializers.FileField):

    def to_representation(self, value):
        if not value:
            return None
        return create_link(value.url, self.context['request'])


class ImageFiledWithLinkRepresentation(serializers.ImageField):
    def to_representation(self, value):
        if not value:
            return None
        return create_link(value.url, self.context['request'])

