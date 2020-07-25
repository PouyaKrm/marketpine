from rest_framework import serializers


class BaseModelSerializerWithRequestObj(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):

        context = kwargs.get('context')
        request = kwargs.get('request')

        if context is not None and context['request'] is not None:
            self.request = context['request']

        elif request is not None:
            self.request = request

        super().__init__(*args, **kwargs)
