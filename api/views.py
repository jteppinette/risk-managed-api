"""
Define the views and viewsets that will handle the REST framework.
"""

from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import mixins

from rest_framework.response import Response
from rest_framework.decorators import detail_route
from rest_framework.views import APIView

from rest_framework.exceptions import AuthenticationFailed

from api.permissions import IsNotAnAdmin, IsNotAnAdministrator, IsNotNationals
from api.permissions import IsCreatingOrAuthenticated, IsAdminOrReadOnly
from api.permissions import IsAdminOrNoDelete
from api.permissions import AdminsNationalsAdministratorsOnlyGet
from api.permissions import NationalsAdministratorsReadOnly

from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout

from api.exceptions import PaymentRequiredViewSet

# Custom User Model
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from api.serializers import UserSerializer

# User Helper Models
from api.models import Organization, University
from api.serializers import OrganizationSerializer, UniversitySerializer
from api.filters import OrganizationFilter, UniversityFilter

# User Profile Models
from api.models import Nationals, Administrator, Host
from api.serializers import NationalsSerializer, AdministratorSerializer
from api.serializers import HostSerializer

# Email Helper Models
from api.models import CarbonCopyAddress
from api.serializers import CarbonCopyAddressSerializer

# Identity Models
from api.models import Identity, Flag
from api.serializers import IdentitySerializer, FlagSerializer
from api.filters import IdentityFilter, FlagFilter

# Event Models
from api.models import Event, Procedure, Invitee
from api.serializers import EventSerializer, ProcedureSerializer, InviteeSerializer
from api.filters import EventFilter, ProcedureFilter, InviteeFilter

# Guest Registration Model
from api.models import GuestRegistration
from api.serializers import GuestRegistrationSerializer
from api.filters import GuestRegistrationFilter

"""
                             CUSTOM USER MODEL
"""


class UserViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides the `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally, the user must be an admin or this rest endpoint cannot
    accept a `DELETE` method.
    """
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdminOrNoDelete)
    filter_fields = ('id', 'username')

    def get_queryset(self):
        """
        If the user is not an admin, only return the current user.
        """
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        else:
            return self.queryset.filter(id=user.id)


class Login(APIView):
    """
    Login a user.
    """
    permission_classes = []

    def post(self, request, format=None):
        """
        Log the user in, then return the `User` object.
        """
        username = request.data['username']
        password = request.data['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response(UserSerializer(user).data)
        else:
            raise AuthenticationFailed()


class Logout(APIView):
    """
    Logout a user.
    """
    permission_classes = []

    def get(self, request, format=None):
        """
        Log the user out.
        """
        logout(request)
        return Response('Water Dragon')

"""
                             USER HELPER MODELS
"""


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides the `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally, the user must be an admin or this rest endpoint will be read
    only.
    """
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdminOrReadOnly)
    filter_class = OrganizationFilter


class UniversityViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides the `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally, the user must be an admin or this rest endpoint will be read
    only.
    """
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = (permissions.IsAuthenticated, IsAdminOrReadOnly)
    filter_class = UniversityFilter

"""
                             USER PROFILE MODELS
"""


class NationalsViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides the `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally, the requesting user cannot be an `Administrator` and the 
    user must be an admin or this rest endpoint cannot accept a `DELETE`
    method. Also, if the user is not creating, they must be authenticated.
    """
    queryset = Nationals.objects.all()
    serializer_class = NationalsSerializer
    permission_classes = (IsCreatingOrAuthenticated, IsNotAnAdministrator,
                          IsAdminOrNoDelete)

    def get_queryset(self):
        """
        This method performs differently based on the requesting user profile.

        `is_superuser`:
            Return all results

        `Nationals`:
            Return itself

        `Host`:
            Return it's `Nationals` object
        """
        user = self.request.user

        if user.is_superuser:
            return self.queryset
        elif hasattr(user, 'nationals'):
            return self.queryset.filter(user=user)
        elif hasattr(user, 'host'):
            return self.queryset.filter(organization=user.host.organization)


class AdministratorViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides the `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally, the requesting user cannot be a `Nationals` and the 
    user must be an admin or this rest endpoint cannot accept a `DELETE`
    method. Also, if the user is not creating, they must be authenticated.
    """
    queryset = Administrator.objects.all()
    serializer_class = AdministratorSerializer
    permission_classes = (IsCreatingOrAuthenticated, IsNotNationals,
                          IsAdminOrNoDelete)

    def get_queryset(self):
        """
        This method performs differently based on the requesting user profile.

        `is_superuser`:
            Return all results
        
        `Administrator`:
            Return itself

        `Host`:
            Return it's `Administrator` object
        """
        user = self.request.user

        if user.is_superuser:
            return self.queryset
        elif hasattr(user, 'administrator'):
            return self.queryset.filter(user=user)
        elif hasattr(user, 'host'):
            return self.queryset.filter(university=user.host.university)


class HostViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides the `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally, the requesting user must be an admin or this rest endpoint
    cannot accept a `DELETE` method. Also, if the user is not creating, they
    must be authenticated.
    """
    queryset = Host.objects.all()
    serializer_class = HostSerializer
    permission_classes = (IsCreatingOrAuthenticated, IsAdminOrNoDelete)
    filter_fields = ('organization', 'university')

    def get_queryset(self):
        """
        This method performs differently based on the requesting user profile.

        `is_superuser`:
            Return all results

        `Host`:
            Return itself

        `Nationals`:
            Return all `Host` objects owned by the current `Nationals`

        `Administrator`:
            Return all `Host` objects owned by the current `Administrator`
        """
        user = self.request.user

        if user.is_superuser:
            return self.queryset
        elif hasattr(user, 'host'):
            return self.queryset.filter(user=user)
        elif hasattr(user, 'nationals'):
            return self.queryset.filter(nationals=user.nationals)
        elif hasattr(user, 'administrator'):
            return self.queryset.filter(administrator=user.administrator)
        
"""
                             EMAIL HELPER MODELS
"""


class CarbonCopyAddressViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides the `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    queryset = CarbonCopyAddress.objects.all()
    serializer_class = CarbonCopyAddressSerializer
    filter_fields = ('id', 'email')

    def get_queryset(self):
        """
        Return the `CarbonCopyAddresses` that correspond to the current user.
        If the user `is_superuser` return all.
        """
        user = self.request.user

        if user.is_superuser:
            return self.queryset
        else:
            return self.queryset.filter(user=user)

    def perform_create(self, serializer):
        """
        Attach the current `User` to the new object.
        """
        serializer.save(user=self.request.user)

"""
                             IDENTITY MODELS
"""


class IdentityViewSet(mixins.CreateModelMixin,
                      mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      PaymentRequiredViewSet):
    """
    This viewset automatically provides the `list`, `create` and `retreive`
    actions.
    """
    queryset = Identity.objects.all()
    serializer_class = IdentitySerializer
    filter_class = IdentityFilter

    def get_queryset(self):
        """
        Add custom filtering on the `search` query parameter.
        """
        queryset = self.queryset

        # Custom `search` filter
        search = self.request.query_params.get('search', None)

        if search is None:
            return queryset

        search_list = search.split(' ')

        if len(search_list) == 1:
            queryset = queryset.filter(Q(first_name__icontains=search_list[0]) |
                                       Q(last_name__icontains=search_list[0]) |
                                       Q(gender=search_list[0]))
        elif len(search_list) == 2:
            queryset = queryset.filter(Q(first_name__icontains=search_list[0]) |
                                       Q(last_name__icontains=search_list[0]) |
                                       Q(gender=search_list[0]),
                                       Q(first_name__icontains=search_list[1]) |
                                       Q(last_name__icontains=search_list[1]) |
                                       Q(gender=search_list[1]))

        elif len(search_list) == 3:
            queryset = queryset.filter(Q(first_name__icontains=search_list[0]) |
                                       Q(last_name__icontains=search_list[0]) |
                                       Q(gender=search_list[0]),
                                       Q(first_name__icontains=search_list[1]) |
                                       Q(last_name__icontains=search_list[1]) |
                                       Q(gender=search_list[1]),
                                       Q(first_name__icontains=search_list[2]) |
                                       Q(last_name__icontains=search_list[2]) |
                                       Q(gender=search_list[2]))

        return queryset


class FlagViewSet(mixins.CreateModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.ListModelMixin,
                  mixins.UpdateModelMixin,
                  mixins.DestroyModelMixin,
                  PaymentRequiredViewSet):
    """
    This viewset automatically provides the `list`, `create` and `retreive`,
    `update`, and `destroy` actions.
    """
    queryset = Flag.objects.all()
    serializer_class = FlagSerializer
    filter_class = FlagFilter

    def get_queryset(self):
        """
        This method performs differently based on the requesting user profile.

        `is_superuser`:
            Return all `Flag` objects

        `Host`:
            Return all `Flag` objects created by the current `Host`, or
            the current host's `Nationals` or `Administrator`

        `Nationals`:
            Return all `Flag` objects created by itself

        `Administrator`:
            Return all `Flag` objects created by itself
        """
        user = self.request.user
        queryset = None

        if user.is_superuser:
            queryset =  self.queryset
        elif hasattr(user, 'host'):
            queryset =  self.queryset.filter(Q(host=user.host) |
                                        Q(nationals=user.host.nationals) |
                                        Q(administrator=user.host.administrator))
        elif hasattr(user, 'nationals'):
            queryset =  self.queryset.filter(nationals=user.nationals)
        elif hasattr(user, 'administrator'):
            queryset =  self.queryset.filter(administrator=user.administrator)

        # Custom `search` filter
        search = self.request.query_params.get('search', None)

        if search is None:
            return queryset

        search_list = search.split(' ')

        if len(search_list) == 1:
            queryset = queryset.filter(Q(identity__first_name__icontains=search_list[0]) |
                                       Q(identity__last_name__icontains=search_list[0]) |
                                       Q(identity__gender=search_list[0]))
        elif len(search_list) == 2:
            queryset = queryset.filter(Q(identity__first_name__icontains=search_list[0]) |
                                       Q(identity__last_name__icontains=search_list[0]) |
                                       Q(identity__gender=search_list[0]),
                                       Q(identity__first_name__icontains=search_list[1]) |
                                       Q(identity__last_name__icontains=search_list[1]) |
                                       Q(identity__gender=search_list[1]))

        elif len(search_list) == 3:
            queryset = queryset.filter(Q(identity__first_name__icontains=search_list[0]) |
                                       Q(identity__last_name__icontains=search_list[0]) |
                                       Q(identity__gender=search_list[0]),
                                       Q(identity__first_name__icontains=search_list[1]) |
                                       Q(identity__last_name__icontains=search_list[1]) |
                                       Q(identity__gender=search_list[1]),
                                       Q(identity__first_name__icontains=search_list[2]) |
                                       Q(identity__last_name__icontains=search_list[2]) |
                                       Q(identity__gender=search_list[2]))

        return queryset


    def perform_create(self, serializer):
        """
        Set the `reach` and `nationals/administrator/host` based on the
        incoming request object.
        """
        user = self.request.user

        if hasattr(user, 'nationals'):
            serializer.save(nationals=user.nationals, reach='Nationals')
        elif hasattr(user, 'administrator'):
            serializer.save(administrator=user.administrator, reach='Administrator')
        elif hasattr(user, 'host'):
            serializer.save(host=user.host, reach='Host')
        elif user.is_superuser:
            serializer.save(reach='Nationals')


"""
                             EVENT MODELS
"""


class EventViewSet(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.ListModelMixin,
                   PaymentRequiredViewSet):
    """
    This viewset automatically provides the `list`, `create` and  `retrieve`
    actions.
    """
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (permissions.IsAuthenticated,
                          AdminsNationalsAdministratorsOnlyGet)
    filter_class = EventFilter
    ordering = ('-date',)

    
    def get_queryset(self):
        """
        This method performs differently based on the requesting user profile.

        `is_superuser`:
            Return all `Event` objects

        `Host`:
            Return all `Event` objects created by the current `Host`

        `Nationals`:
            Return all `Host` objects create by it's `Host` objects

        `Administrator`:
            Return all `Host` objects create by it's `Host` objects
        """
        user = self.request.user

        if user.is_superuser:
            return self.queryset
        elif hasattr(user, 'host'):
            return self.queryset.filter(host=user.host)
        elif hasattr(user, 'nationals'):
            return self.queryset.filter(host__in=user.nationals.hosts.all())
        elif hasattr(user, 'administrator'):
            return self.queryset.filter(host__in=user.administrator.hosts.all())

    def perform_create(self, serializer):
        """
        Attach the current `Host` to the new object.
        """
        serializer.save(host=self.request.user.host)

    @detail_route(methods=['POST'])
    def end(self, request, pk=None, *args, **kwargs):
        """
        End the event at the current UTC Time.
        """
        event = self.get_object()
        event.end_time = timezone.now()
        event.save()

        serializer = EventSerializer(event)

        return Response(serializer.data)


class ProcedureViewSet(mixins.RetrieveModelMixin,
                       mixins.ListModelMixin,
                       PaymentRequiredViewSet):
    """
    This viewset automatically provides the `list`, `retrieve` actions.
    """
    queryset = Procedure.objects.all()
    serializer_class = ProcedureSerializer
    filter_class = ProcedureFilter
    ordering = ('-completion_time',)
    
    def get_queryset(self):
        """
        This method performs differently based on the requesting user profile.

        `is_superuser`:
            Return all `Procedure` objects

        `Host`:
            Return all `Procedure` objects created by the current `Host`

        `Nationals`:
            Return all `Procedure` objects created by it's `Host` objects

        `Administrator`:
            Return all `Procedure` objects created by it's `Host` objects
        """
        user = self.request.user

        if user.is_superuser:
            return self.queryset
        elif hasattr(user, 'host'):
            return self.queryset.filter(event__host=user.host)
        elif hasattr(user, 'nationals'):
            hosts = user.nationals.hosts.all()
            return self.queryset.filter(event__host__in=hosts)
        elif hasattr(user, 'administrator'):
            hosts = user.administrator.hosts.all()
            return self.queryset.filter(event__host__in=hosts)

    @detail_route(methods=['POST'])
    def complete(self, request, pk=None, *args, **kwargs):
        """
        Complete the `Procedure` at the current UTC Time.
        """
        procedure = self.get_object()
        procedure.completion_time = timezone.now()
        procedure.save()

        serializer = ProcedureSerializer(procedure)

        return Response(serializer.data)


class InviteeViewSet(mixins.CreateModelMixin,
                     mixins.RetrieveModelMixin,
                     mixins.ListModelMixin,
                     mixins.DestroyModelMixin,
                     PaymentRequiredViewSet):
    """
    This viewset automatically provides the `create`, `list`, `retrieve`, and
    `destroy` actions.
    """
    queryset = Invitee.objects.all()
    serializer_class = InviteeSerializer
    permission_classes = (permissions.IsAuthenticated, NationalsAdministratorsReadOnly)
    filter_class = InviteeFilter
    
    def get_queryset(self):
        """
        This method performs differently based on the requesting user profile.

        `is_superuser`:
            Return all `Invitee` objects

        `Host`:
            Return all `Invitee` objects created by the current `Host`

        `Nationals`:
            Return all `Invitee` objects created by it's `Host` objects

        `Administrator`:
            Return all `Invitee` objects created by it's `Host` objects
        """
        user = self.request.user
        queryset = None

        if user.is_superuser:
            queryset = self.queryset
        elif hasattr(user, 'host'):
            queryset = self.queryset.filter(event__host=user.host)
        elif hasattr(user, 'nationals'):
            hosts = user.nationals.hosts.all()
            queryset =  self.queryset.filter(event__host__in=hosts)
        elif hasattr(user, 'administrator'):
            hosts = user.administrator.hosts.all()
            queryset = self.queryset.filter(event__host__in=hosts)

        # Custom `name` filter
        name = self.request.query_params.get('name', None)

        if name is None:
            return queryset

        name_list = name.split(' ')

        if len(name_list) == 1:
            queryset = queryset.filter(Q(first_name__icontains=name_list[0]) |
                                       Q(last_name__icontains=name_list[0]))
        elif len(name_list) == 2:
            queryset = queryset.filter(Q(first_name__icontains=name_list[0]) |
                                       Q(last_name__icontains=name_list[0]),
                                       Q(first_name__icontains=name_list[1]) |
                                       Q(last_name__icontains=name_list[1]))

        return queryset

"""
                             GUEST REGISTRATION MODEL
"""


class GuestRegistrationViewSet(mixins.CreateModelMixin,
                               mixins.RetrieveModelMixin,
                               mixins.ListModelMixin,
                               PaymentRequiredViewSet):
    """
    This viewset automatically provides the `list`, `create` and  `retrieve`
    actions.
    """
    queryset = GuestRegistration.objects.all()
    serializer_class = GuestRegistrationSerializer
    permission_classes = (permissions.IsAuthenticated,
                          NationalsAdministratorsReadOnly)
    filter_class = GuestRegistrationFilter
    ordering = ('-date_time_taken',)
    
    def get_queryset(self):
        """
        This method performs differently based on the requesting user profile.

        `is_superuser`:
            Return all `GuestRegistration` objects

        `Host`:
            Return all `GuestRegistration` objects created by the current `Host`

        `Nationals`:
            Return all `GuestRegistration` objects created by it's `Host` objects

        `Administrator`:
            Return all `GuestRegistration` objects created by it's `Host` objects
        """
        user = self.request.user
        queryset = None

        if user.is_superuser:
            queryset = self.queryset
        elif hasattr(user, 'host'):
            queryset = self.queryset.filter(event__host=user.host)
        elif hasattr(user, 'nationals'):
            queryset = self.queryset.filter(event__host__in=user.nationals.hosts.all())
        elif hasattr(user, 'administrator'):
            queryset = self.queryset.filter(event__host__in=user.administrator.hosts.all())

        # Custom `search` filter
        search = self.request.query_params.get('search', None)

        if search is None:
            pass
        else:
            search_list = search.split(' ')

            if len(search_list) == 1:
                queryset = queryset.filter(Q(identity__first_name__icontains=search_list[0]) |
                                           Q(identity__last_name__icontains=search_list[0]) |
                                           Q(identity__gender=search_list[0]))
            elif len(search_list) == 2:
                queryset = queryset.filter(Q(identity__first_name__icontains=search_list[0]) |
                                           Q(identity__last_name__icontains=search_list[0]) |
                                           Q(identity__gender=search_list[0]),
                                           Q(identity__first_name__icontains=search_list[1]) |
                                           Q(identity__last_name__icontains=search_list[1]) |
                                           Q(identity__gender=search_list[1]))

            elif len(search_list) == 3:
                queryset = queryset.filter(Q(identity__first_name__icontains=search_list[0]) |
                                           Q(identity__last_name__icontains=search_list[0]) |
                                           Q(identity__gender=search_list[0]),
                                           Q(identity__first_name__icontains=search_list[1]) |
                                           Q(identity__last_name__icontains=search_list[1]) |
                                           Q(identity__gender=search_list[1]),
                                           Q(identity__first_name__icontains=search_list[2]) |
                                           Q(identity__last_name__icontains=search_list[2]) |
                                           Q(identity__gender=search_list[2]))

        # Custom `unique` filter
        unique = self.request.query_params.get('unique', None)
        
        if unique is None:
            pass
        else:
            queryset = queryset.distinct(str(unique))

        return queryset
