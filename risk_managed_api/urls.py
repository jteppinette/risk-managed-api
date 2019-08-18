from django.conf.urls import include, url
from django.contrib import admin

from rest_framework.routers import DefaultRouter

from risk_managed_api import views

router = DefaultRouter()

router.register("users", views.UserViewSet)
router.register("organizations", views.OrganizationViewSet)
router.register("universities", views.UniversityViewSet)
router.register("nationals", views.NationalsViewSet)
router.register("administrators", views.AdministratorViewSet)
router.register("hosts", views.HostViewSet)
router.register("carboncopyaddresses", views.CarbonCopyAddressViewSet)
router.register("identities", views.IdentityViewSet)
router.register("flags", views.FlagViewSet)
router.register("events", views.EventViewSet)
router.register("procedures", views.ProcedureViewSet)
router.register("invitees", views.InviteeViewSet)
router.register("guestregistrations", views.GuestRegistrationViewSet)

urlpatterns = [
    url("^browsable-auth/", include("rest_framework.urls", namespace="rest_framework")),
    url("^login/$", views.Login.as_view()),
    url("^logout/$", views.Logout.as_view()),
    url("^admin/", admin.site.urls),
]

urlpatterns += router.urls
