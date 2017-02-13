"""
Define the routes that will be used in moving throughout the REST api.
"""

from django.conf.urls import url, include
from django.contrib import admin

from api import views

from rest_framework.routers import DefaultRouter

"""
The routers defined below deciphers the view sets to create each of the
`action` methods required by REST. 

After deciding on what view should go with what HTTP method, the routes are
included in `urlpatterns'.
"""

router = DefaultRouter()

# Custom User Model
router.register('users', views.UserViewSet)

# User Helper Models
router.register('organizations', views.OrganizationViewSet)
router.register('universities', views.UniversityViewSet)

# User Profile Models
router.register('nationals', views.NationalsViewSet)
router.register('administrators', views.AdministratorViewSet)
router.register('hosts', views.HostViewSet)

# Email Helper Models
router.register('carboncopyaddresses', views.CarbonCopyAddressViewSet)

# Identity Models
router.register('identities', views.IdentityViewSet)
router.register('flags', views.FlagViewSet)

# Event Models
router.register('events', views.EventViewSet)
router.register('procedures', views.ProcedureViewSet)
router.register('invitees', views.InviteeViewSet)

# Guest Registration Model
router.register('guestregistrations', views.GuestRegistrationViewSet)

urlpatterns = [
    url('^browsable-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url('^login/$', views.Login.as_view()),
    url('^logout/$', views.Logout.as_view()),
    url('^admin/', admin.site.urls),
]

urlpatterns += router.urls
