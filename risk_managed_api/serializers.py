from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from rest_framework import serializers

from risk_managed_api.models import (
    Administrator,
    CarbonCopyAddress,
    Event,
    Flag,
    GuestRegistration,
    Host,
    Identity,
    Invitee,
    Nationals,
    Organization,
    Procedure,
    University,
)
from risk_managed_api.utils.serializers import HyperlinkedImageField


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def update(self, instance, validated_data):
        instance.username = validated_data.get("username", instance.username)
        try:
            instance.set_password(validated_data["password"])
        except Exception:
            pass
        instance.save()
        return instance

    def create(self, validated_data):
        user = get_user_model()(username=validated_data["username"])
        user.set_password(validated_data["password"])
        user.save()
        return user

    def to_representation(self, obj):
        payload = super(UserSerializer, self).to_representation(obj)
        profile_type = ""
        if obj.is_superuser:
            profile_type = "Superuser"
        elif hasattr(obj, "nationals"):
            profile_type = "Nationals"
        elif hasattr(obj, "administrator"):
            profile_type = "Administrator"
        elif hasattr(obj, "host"):
            profile_type = "Host"
        else:
            profile_type = None

        payload["profile"] = profile_type
        return payload


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ("id", "name")


class UniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ("id", "name", "acronym", "state", "longitude", "latitude")


class UserProfileSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        fields_to_save = self.__class__.Meta.fields_to_save

        # Removes the source location from the username
        # This allows the json to be sent as 'username' not 'user.username'
        try:
            validated_data["username"] = validated_data["user"]["username"]
        except Exception:
            pass

        instance.user.username = validated_data.get("username", instance.user.username)
        try:
            instance.user.set_password(validated_data["password"])
        except Exception:
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
            validated_data["username"] = validated_data["user"]["username"]
        except Exception:
            pass

        serializer = UserSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        obj = self.__class__.Meta.model(user=user)

        # Set all needed attributes described in `fields_to_save`
        for field in fields_to_save:
            setattr(obj, field, validated_data.get(field, None))
        obj.save()
        return obj


class NationalsSerializer(UserProfileSerializer):
    username = serializers.CharField(max_length=80, source="user.username")
    password = serializers.CharField(max_length=80, write_only=True)

    class Meta:
        model = Nationals
        fields = "__all__"
        read_only_fields = ("user", "enabled")
        fields_to_save = ["organization"]

    def to_representation(self, obj):
        payload = super(NationalsSerializer, self).to_representation(obj)

        payload["organization"] = OrganizationSerializer(obj.organization).data

        return payload


class AdministratorSerializer(UserProfileSerializer):
    username = serializers.CharField(max_length=80, source="user.username")
    password = serializers.CharField(max_length=80, write_only=True)

    class Meta:
        model = Administrator
        fields = "__all__"
        read_only_fields = ("user", "enabled")
        fields_to_save = ["university"]

    def to_representation(self, obj):
        payload = super(AdministratorSerializer, self).to_representation(obj)

        payload["university"] = UniversitySerializer(obj.university).data

        return payload


class HostSerializer(UserProfileSerializer):
    username = serializers.CharField(max_length=80, source="user.username")
    password = serializers.CharField(max_length=80, write_only=True)

    class Meta:
        model = Host
        fields = "__all__"
        read_only_fields = ("user", "enabled")
        fields_to_save = ["organization", "university", "nationals", "administrator"]

    def to_representation(self, obj):
        payload = super(HostSerializer, self).to_representation(obj)

        payload["organization"] = OrganizationSerializer(obj.organization).data
        payload["university"] = UniversitySerializer(obj.university).data

        return payload


class CarbonCopyAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarbonCopyAddress
        fields = ("id", "user", "email")
        read_only_fields = ("user",)


class IdentitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Identity
        fields = "__all__"


class FlagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flag
        fields = "__all__"
        read_only_fields = ("reach",)


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = "__all__"
        read_only_fields = ("host", "start_time", "end_time")


class ProcedureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedure
        fields = "__all__"
        read_only = ("description", "completion_time", "event")


class InviteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitee
        fields = "__all__"


class GuestRegistrationSerializer(serializers.ModelSerializer):
    image = HyperlinkedImageField()

    class Meta:
        model = GuestRegistration
        fields = "__all__"
        read_only_fields = ("date_time_taken",)
