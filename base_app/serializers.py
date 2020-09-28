import ast

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


class MultipartRequestBodyDictFiled(serializers.Field):

    def __init__(self, max_items: int):
        super().__init__()
        self.max_items = max_items

    def to_internal_value(self, data) -> dict:
        if type(data) != str or len(data) > 200:
            raise serializers.ValidationError("invalid field")
        try:
            result = ast.literal_eval(data)
            if type(result) != dict:
                raise serializers.ValidationError("inavlid dictionary")
            return self._validate_items(result)
        except (SyntaxError, ValueError):
            raise serializers.ValidationError("invalid field")

    def _validate_items(self, id_show_orders: dict):
        if len(id_show_orders) > self.max_items:
            raise serializers.ValidationError("invalid field")
        parsed_dict = {}
        for k, v in id_show_orders.items():
            try:
                k_int = int(k)
                v_int = int(v)
                if k_int <= 0:
                    raise serializers.ValidationError("{} is invalid id value".format(k_int))
                parsed_dict[k_int] = v_int
            except ValueError:
                raise serializers.ValidationError("field contains un parsable to int values")

        return parsed_dict

