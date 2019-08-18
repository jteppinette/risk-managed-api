from rest_framework import serializers


class HyperlinkedImageField(serializers.ImageField):
    def to_representation(self, value):
        request = self.context.get("request", None)
        return request.build_absolute_uri(value.url)
