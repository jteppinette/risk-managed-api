"""
This module defines the serializers that will used to transform a Django model
into the proper formats required by the Django REST Framework.
"""

from django.forms import widgets
from django.conf import settings
from django.contrib.auth.models import User

from rest_framework import serializers

from api.utils.serializers import HyperlinkedImageField

# Custom User Model
from django.contrib.auth import get_user_model

# User Helper Models
from api.models import Organization, University

# User Profile Models
from api.utils.serializers import UserProfileSerializer
from api.models import Nationals, Administrator, Host

# Email Helper Models
from api.models import CarbonCopyAddress

# Identity Models
from api.models import Identity, Flag

# Event Models
from api.models import Event, Procedure, Invitee

# Guest Registration Model
from api.models import GuestRegistration

"""
                             CUSTOM USER MODEL
"""


class UserSerializer(serializers.ModelSerializer):
    """
    Serialize a `User` model into the proper format.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):
        """
        Update a `User` object and update it's password using `set_password` if
        a password is sent.
        """
        instance.username = validated_data.get('username', instance.username)
        try:
            instance.set_password(validated_data['password'])
        except:
            pass
        instance.save()
        return instance

    def create(self, validated_data):
        """
        Create a `User` object and set it's password using `set_password`.
        """
        user = get_user_model()(username=validated_data['username'])
        user.set_password(validated_data['password'])
        user.save()
        return user

    def to_representation(self, obj):
        """
        Add the profile type to the final payload.
        """
        payload = super(UserSerializer, self).to_representation(obj)
        profile_type = ''
        if obj.is_superuser:
            profile_type = 'Superuser'
        elif hasattr(obj, 'nationals'):
            profile_type = 'Nationals'
        elif hasattr(obj, 'administrator'):
            profile_type = 'Administrator'
        elif hasattr(obj, 'host'):
            profile_type = 'Host'
        else:
            profile_type = None

        payload['profile'] = profile_type
        return payload

"""
                             USER HELPER MODELS
"""


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Serialize an `Organization` model into the proper format.
    """
    class Meta:
        model = Organization
        fields = ('id', 'name')


class UniversitySerializer(serializers.ModelSerializer):
    """
    Serialize a `University` model into the proper format.
    """
    class Meta:
        model = University
        fields = ('id', 'name', 'acronym', 'state', 'longitude', 'latitude')

"""
                             USER PROFILE MODELS
"""


class NationalsSerializer(UserProfileSerializer):
    """
    Serialize a `Nationals` model into the proper format.
    """
    username = serializers.CharField(max_length=80, source='user.username')
    password = serializers.CharField(max_length=80, write_only=True)

    class Meta:
        model = Nationals 
        fields = ('__all__')
        read_only_fields = ('user', 'enabled')
        fields_to_save = ['organization']

    def to_representation(self, obj):
        """
        Add `Organization` to the final payload.
        """
        payload = super(NationalsSerializer, self).to_representation(obj)

        payload['organization'] = OrganizationSerializer(obj.organization).data

        return payload


class AdministratorSerializer(UserProfileSerializer):
    """
    Serialize an `Administrator` model into the proper format.
    """
    username = serializers.CharField(max_length=80, source='user.username')
    password = serializers.CharField(max_length=80, write_only=True)

    class Meta:
        model = Administrator
        fields = ('__all__')
        read_only_fields = ('user', 'enabled')
        fields_to_save = ['university']

    def to_representation(self, obj):
        """
        Add `University` to the final payload.
        """
        payload = super(AdministratorSerializer, self).to_representation(obj)

        payload['university'] = UniversitySerializer(obj.university).data

        return payload


class HostSerializer(UserProfileSerializer):
    """
    Serialize a `Host` model into the proper format.
    """
    username = serializers.CharField(max_length=80, source='user.username')
    password = serializers.CharField(max_length=80, write_only=True)

    class Meta:
        model = Host
        fields = ('__all__')
        read_only_fields = ('user', 'enabled')
        fields_to_save = ['organization', 'university',
                          'nationals', 'administrator']

    def to_representation(self, obj):
        """
        Add `Organization` and `University` to the final payload.
        """
        payload = super(HostSerializer, self).to_representation(obj)

        payload['organization'] = OrganizationSerializer(obj.organization).data
        payload['university'] = UniversitySerializer(obj.university).data

        return payload

"""
                             EMAIL HELPER MODELS
"""


class CarbonCopyAddressSerializer(serializers.ModelSerializer):
    """
    Serialize a `CarbonCopyAddress` model into the proper format.
    """
    class Meta:
        model = CarbonCopyAddress
        fields = ('id', 'user', 'email')
        read_only_fields = ('user',)

"""
                             IDENTITY MODELS
"""


class IdentitySerializer(serializers.ModelSerializer):
    """
    Serialize an `Identity` model into the proper format.
    """
    class Meta:
        model = Identity
        fields = ('__all__')


class FlagSerializer(serializers.ModelSerializer):
    """
    Serialize a `Flag` model into the proper format.
    """
    class Meta:
        model = Flag
        fields = ('__all__')
        read_only_fields = ('reach',)

"""
                             EVENT MODELS
"""


class EventSerializer(serializers.ModelSerializer):
    """
    Serialize an `Event` model into the proper format.
    """
    class Meta:
        model = Event
        fields = ('__all__')
        read_only_fields = ('host', 'start_time', 'end_time')


class ProcedureSerializer(serializers.ModelSerializer):
    """
    Serialize a `Procedure` model into the proper format.
    """
    class Meta:
        model = Procedure
        fields = ('__all__')
        read_only = ('description', 'completion_time', 'event')


class InviteeSerializer(serializers.ModelSerializer):
    """
    Serialize an `Invitee` model into the proper format.
    """
    class Meta:
        model = Invitee
        fields = ('__all__')

"""
                             GUEST REGISTRATION MODEL
"""


class GuestRegistrationSerializer(serializers.ModelSerializer):
    """
    Serialize a `GuestRegistration` model into the proper format.
    """
    image = HyperlinkedImageField()
    thumbnail = HyperlinkedImageField(read_only=True)

    class Meta:
        model = GuestRegistration
        fields = ('__all__')
        read_only_fields = ('date_time_taken',)
