from django.contrib import admin

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


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ["name"]


class UniversityAdmin(admin.ModelAdmin):
    list_display = ("name", "acronym", "state", "longitude", "latitude")
    search_fields = ["name", "acronym", "state"]


class NationalsAdmin(admin.ModelAdmin):
    list_display = ("organization", "user", "enabled", "number_of_hosts")
    list_filter = ("enabled",)
    search_fields = ["organization__name", "user__username", "user__username"]


class AdministratorAdmin(admin.ModelAdmin):

    list_display = ("university", "user", "enabled", "number_of_hosts")
    list_filter = ("enabled",)
    search_fields = ["university__name", "university__acronym", "user__username", "user__username"]


class HostAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "organization",
        "user",
        "has_administrator",
        "has_nationals",
        "enabled",
    )
    list_filter = ("enabled",)
    search_fields = ["organization__name", "user__username", "user__username"]


class CarbonCopyAddressAdmin(admin.ModelAdmin):
    list_display = ("email", "user")
    search_fields = ["email", "user__username"]


class IdentityAdmin(admin.ModelAdmin):
    list_display = ("__str__", "gender", "dob")
    search_fields = ["first_name", "last_name", "gender", "dob"]


class FlagAdmin(admin.ModelAdmin):
    list_display = ("__str__", "reach", "creator", "violation", "other")
    search_fields = [
        "identity__first_name",
        "identity__last_name",
        "identity__gender",
        "reach",
        "violation",
        "other",
    ]


class EventAdmin(admin.ModelAdmin):
    list_display = ("host", "name", "date")
    search_fields = ["host__username", "host_organization", "host_university", "name"]


class ProcedureAdmin(admin.ModelAdmin):
    list_display = ("event", "description", "completion_time")
    search_fields = [
        "description",
        "event__name",
        "event__host__organization__name",
        "event__host__university__name",
    ]


class InviteeAdmin(admin.ModelAdmin):
    list_display = ("event", "first_name", "last_name", "gender")
    search_fields = [
        "first_name",
        "last_name",
        "gender",
        "event__name",
        "event__host__organization__name",
        "event__host__university__name",
    ]


class GuestRegistrationAdmin(admin.ModelAdmin):
    list_display = ("identity", "event", "date_time_taken")
    search_fields = [
        "identity__first_name",
        "identity__last_name",
        "identity__gender",
        "event__host__organization",
        "event__host__university",
        "event__name",
    ]


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
