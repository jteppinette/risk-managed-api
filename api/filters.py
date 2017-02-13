"""
This module defines the filters that will used to query the rest framework.
"""

import django_filters

# Custom User Model
from django.contrib.auth import get_user_model

# User Helper Models
from api.models import Organization, University

# User Profile Models
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
                             USER HELPER MODELS
"""


class OrganizationFilter(django_filters.FilterSet):
    """
    Configure how a user should be able to filter this model.
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Organization
        fields = ['id']


class UniversityFilter(django_filters.FilterSet):
    """
    Configure how a user should be able to filter this model.
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    acryonym = django_filters.CharFilter(lookup_expr='iexact')
    state = django_filters.CharFilter(lookup_expr='iexact')
    
    class Meta:
        model = University
        fields = ['id']


"""
                             IDENTITY MODELS
"""


class IdentityFilter(django_filters.FilterSet):
    """
    Configure how a user should be able to filter this model.
    """
    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Identity
        fields = ['id', 'gender', 'dob']


class FlagFilter(django_filters.FilterSet):
    """
    Configure how a user should be able to filter this model.
    """
    first_name = django_filters.CharFilter(name='identity__first_name', lookup_expr='icontains')
    last_name = django_filters.CharFilter(name='identity__last_name', lookup_expr='icontains')
    gender = django_filters.CharFilter(name='identity__gender')
    dob = django_filters.DateFilter(name='identity__dob')

    class Meta:
        model = Flag
        fields = ['id', 'nationals', 'administrator', 'host', 'identity']

"""
                             EVENT MODELS
"""


class EventFilter(django_filters.FilterSet):
    """
    Configure how a user should be able to filter this model.
    """
    name = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Event
        fields = ['id']


class ProcedureFilter(django_filters.FilterSet):
    """
    Configure how a user should be able to filter this model.
    """
    host = django_filters.CharFilter(name='event__host')

    class Meta:
        model = Procedure
        fields = ['id', 'event']


class InviteeFilter(django_filters.FilterSet):
    """
    Configure how a user should be able to filter this model.
    """
    host = django_filters.CharFilter(name='event__host')

    first_name = django_filters.CharFilter(lookup_expr='icontains')
    last_name = django_filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Invitee
        fields = ['id', 'event', 'gender']

"""
                             GUEST REGISTRATION
"""


class GuestRegistrationFilter(django_filters.FilterSet):
    """
    Configure how a user should be able to filter this model.
    """
    first_name = django_filters.CharFilter(name='identity__first_name', lookup_expr='icontains')
    last_name = django_filters.CharFilter(name='identity__last_name', lookup_expr='icontains')
    gender = django_filters.CharFilter(name='identity__gender')
    dob = django_filters.DateFilter(name='identity__dob')

    class Meta:
        model = GuestRegistration
        fields = ['id', 'event', 'identity']
