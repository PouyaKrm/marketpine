from rest_framework import serializers


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


class BaseModelSerializerWithRequestObj(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):
        self.request = get_request_obj(*args, **kwargs)
        kw = pop_request_if_exist(**kwargs)
        super().__init__(*args, **kw)


class BaseSerializerWithRequestObj(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        self.request = get_request_obj(*args, **kwargs)
        kw = pop_request_if_exist(**kwargs)
        super().__init__(*args, **kw)
