"""
This module defines the admin page for the api Django app.
"""

from django.contrib import admin

# User Helper Models
from api.models import Organization, University

# User Profile Models
from api.models import Nationals, Administrator, Host

# Email Helper Models
from api.models import CarbonCopyAddress

# Identity Model
from api.models import Identity, Flag

# Event Models
from api.models import Event, Procedure, Invitee

# Guest Registration Model
from api.models import GuestRegistration

"""
                             USER HELPER MODELS
"""


class OrganizationAdmin(admin.ModelAdmin):
    """
    Provide the `Organization` admin page with special characteristics.
    """
    list_display = ('name',)
    search_fields = ['name']


class UniversityAdmin(admin.ModelAdmin):
    """
    Provide the `University` admin page with special characteristics.
    """
    list_display = ('name', 'acronym', 'state', 'longitude', 'latitude')
    search_fields = ['name', 'acronym', 'state']

"""
                             USER PROFILE MODELS
"""


class NationalsAdmin(admin.ModelAdmin):
    """
    Provide the `Nationals` admin page with special characteristics.
    """
    list_display = ('organization', 'user', 'enabled', 'number_of_hosts')
    list_filter = ('enabled',)
    search_fields = ['organization__name', 'user__username', 'user__username']


class AdministratorAdmin(admin.ModelAdmin):
    """
    Provide the `Administrator` admin page with special characteristics.
    """
    list_display = ('university', 'user', 'enabled', 'number_of_hosts')
    list_filter = ('enabled',)
    search_fields = ['university__name', 'university__acronym',
                     'user__username', 'user__username']


class HostAdmin(admin.ModelAdmin):
    """
    Provide the `Host` admin page with special characteristics.
    """
    list_display = ('__unicode__', 'organization', 'user', 
                    'has_administrator', 'has_nationals', 'enabled')
    list_filter = ('enabled',)
    search_fields = ['organization__name', 'user__username', 'user__username']

"""
                             EMAIL HELPER MODELS
"""


class CarbonCopyAddressAdmin(admin.ModelAdmin):
    """
    Provide the `CarbonCopyAddress` admin page with special characteristics.
    """
    list_display = ('email', 'user')
    search_fields = ['email', 'user__username']

"""
                             IDENTITY MODELS
"""


class IdentityAdmin(admin.ModelAdmin):
    """
    Provide the `Identity` admin page with special characteristics.
    """
    list_display = ('__unicode__', 'gender', 'dob')
    search_fields = ['first_name', 'last_name', 'gender', 'dob']


class FlagAdmin(admin.ModelAdmin):
    """
    Provide the `Flag` admin page with special characteristics.
    """
    list_display = ('__unicode__', 'reach', 'creator', 'violation', 'other')
    search_fields = ['identity__first_name', 'identity__last_name', 'identity__gender',
                     'reach', 'violation', 'other']

"""
                             EVENT MODELS
"""


class EventAdmin(admin.ModelAdmin):
    """
    Provide the `Event` admin page with special characteristics.
    """
    list_display = ('host', 'name', 'date')
    search_fields = ['host__username', 'host_organization', 'host_university', 'name']


class ProcedureAdmin(admin.ModelAdmin):
    """
    Provide the `Procedure` admin page with special charachteristics.
    """
    list_display = ('event', 'description', 'completion_time')
    search_fields = ['description', 'event__name', 'event__host__organization__name',
                     'event__host__university__name']


class InviteeAdmin(admin.ModelAdmin):
    """
    Provide the `Invitee` admin page with special charachteristics.
    """
    list_display = ('event', 'first_name', 'last_name', 'gender')
    search_fields = ['first_name', 'last_name', 'gender', 'event__name',
                     'event__host__organization__name', 'event__host__university__name']

"""
                             GUEST REGISTRATION MODELS
"""


class GuestRegistrationAdmin(admin.ModelAdmin):
    """
    Provide the `GuestRegistration` admin page with special characteristics.
    """
    list_display = ('identity', 'event', 'date_time_taken')
    search_fields = ['identity__first_name', 'identity__last_name', 'identity__gender',
                     'event__host__organization', 'event__host__university', 'event__name']

"""
Register the `ModelAdmin` classes defined above with the django `admin` app.
"""
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(University, UniversityAdmin)

admin.site.register(Nationals, NationalsAdmin)
admin.site.register(Administrator, AdministratorAdmin)
admin.site.register(Host, HostAdmin)

admin.site.register(CarbonCopyAddress, CarbonCopyAddressAdmin)

admin.site.register(Identity, IdentityAdmin)
admin.site.register(Flag, FlagAdmin)

admin.site.register(Event, EventAdmin)
admin.site.register(Procedure, ProcedureAdmin)
admin.site.register(Invitee, InviteeAdmin)

admin.site.register(GuestRegistration, GuestRegistrationAdmin)
