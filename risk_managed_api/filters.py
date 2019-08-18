from django.db import models

import django_filters

from risk_managed_api.models import (
    Event,
    Flag,
    GuestRegistration,
    Host,
    Identity,
    Invitee,
    Organization,
    Procedure,
    University,
)


class OrganizationFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Organization
        fields = ["id"]


class HostFilter(django_filters.FilterSet):
    class Meta:
        model = Host
        fields = ["organization", "university"]
        filter_overrides = {models.ForeignKey: {"filter_class": django_filters.NumberFilter}}


class UniversityFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")
    acryonym = django_filters.CharFilter(lookup_expr="iexact")
    state = django_filters.CharFilter(lookup_expr="iexact")

    class Meta:
        model = University
        fields = ["id"]


class IdentityFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(lookup_expr="icontains")
    last_name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Identity
        fields = ["id", "gender", "dob"]


class FlagFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(
        field_name="identity__first_name", lookup_expr="icontains"
    )
    last_name = django_filters.CharFilter(field_name="identity__last_name", lookup_expr="icontains")
    gender = django_filters.CharFilter(field_name="identity__gender")
    dob = django_filters.DateFilter(field_name="identity__dob")

    class Meta:
        model = Flag
        fields = ["id", "nationals", "administrator", "host", "identity"]
        filter_overrides = {models.ForeignKey: {"filter_class": django_filters.NumberFilter}}


class EventFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Event
        fields = ["id"]


class ProcedureFilter(django_filters.FilterSet):
    host = django_filters.CharFilter(field_name="event__host")

    class Meta:
        model = Procedure
        fields = ["id", "event"]
        filter_overrides = {models.ForeignKey: {"filter_class": django_filters.NumberFilter}}


class InviteeFilter(django_filters.FilterSet):
    host = django_filters.CharFilter(field_name="event__host")

    first_name = django_filters.CharFilter(lookup_expr="icontains")
    last_name = django_filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Invitee
        fields = ["id", "event", "gender"]
        filter_overrides = {models.ForeignKey: {"filter_class": django_filters.NumberFilter}}


class GuestRegistrationFilter(django_filters.FilterSet):
    first_name = django_filters.CharFilter(
        field_name="identity__first_name", lookup_expr="icontains"
    )
    last_name = django_filters.CharFilter(field_name="identity__last_name", lookup_expr="icontains")
    gender = django_filters.CharFilter(field_name="identity__gender")
    dob = django_filters.DateFilter(field_name="identity__dob")

    class Meta:
        model = GuestRegistration
        fields = ["id", "event", "identity"]
        filter_overrides = {models.ForeignKey: {"filter_class": django_filters.NumberFilter}}
