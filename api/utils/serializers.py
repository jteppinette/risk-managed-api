"""
This module provides a utility serializer for user profiles.
"""

from rest_framework import serializers

from django.contrib.auth import get_user_model
import api.serializers

"""
                        HYPERLINKED IMAGE FIELD
"""


class HyperlinkedImageField(serializers.ImageField):
    """
    Override the `ImageField` to provide the fully qualified absolute url.
    """
    def to_representation(self, value):
        """
        Return the absolute url.
        """
        request = self.context.get('request', None)
        return request.build_absolute_uri(value.url)

"""
                        USER PROFILE SERIALIZER
"""


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Abstract the the functionality needed by user profiles to allow the api
    user to interact with `User` objects through user profiles.
    """
    
    def update(self, instance, validated_data):
        fields_to_save = self.__class__.Meta.fields_to_save

        # Removes the source location from the username
        # This allows the json to be sent as 'username' not 'user.username'
        try:
            validated_data['username'] = validated_data['user']['username']
        except:
            pass

        instance.user.username = validated_data.get('username', instance.user.username)
        try:
            instance.user.set_password(validated_data['password'])
        except:
            pass
        instance.user.save()
         
        for field in fields_to_save:
            setattr(instance, field, validated_data.get(field, getattr(instance, field)))
        instance.save()
        return instance


    def create(self, validated_data):
        fields_to_save = self.__class__.Meta.fields_to_save

        # Removes the source location from the username
        # This allows the json to be sent as 'username' not 'user.username'
        try:
            validated_data['username'] = validated_data['user']['username']
        except:
            pass

        serializer = api.serializers.UserSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        obj = self.__class__.Meta.model(user=user)

        # Set all needed attributes described in `fields_to_save`
        for field in fields_to_save:
            setattr(obj, field, validated_data.get(field, None))
        obj.save()
        return obj
