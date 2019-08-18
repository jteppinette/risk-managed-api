from django.contrib.auth import authenticate, get_user_model, login, logout
from django.db.models import Q
from django.utils import timezone

from rest_framework import mixins, permissions, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView

from risk_managed_api.exceptions import PaymentRequiredViewSet
from risk_managed_api.filters import (
    EventFilter,
    FlagFilter,
    GuestRegistrationFilter,
    HostFilter,
    IdentityFilter,
    InviteeFilter,
    OrganizationFilter,
    ProcedureFilter,
    UniversityFilter,
)
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
from risk_managed_api.permissions import (
    AdminsNationalsAdministratorsOnlyGet,
    IsAdminOrNoDelete,
    IsAdminOrReadOnly,
    IsCreatingOrAuthenticated,
    IsNotAnAdministrator,
    IsNotNationals,
    NationalsAdministratorsReadOnly,
)
from risk_managed_api.serializers import (
    AdministratorSerializer,
    CarbonCopyAddressSerializer,
    EventSerializer,
    FlagSerializer,
    GuestRegistrationSerializer,
    HostSerializer,
    IdentitySerializer,
    InviteeSerializer,
    NationalsSerializer,
    OrganizationSerializer,
    ProcedureSerializer,
    UniversitySerializer,
    UserSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdminOrNoDelete)
    filterset_fields = ("id", "username")

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return self.queryset
        else:
            return self.queryset.filter(id=user.id)


class Login(APIView):
    permission_classes = []

    def post(self, request, format=None):
        username = request.data["username"]
        password = request.data["password"]

        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return Response(UserSerializer(user).data)
        else:
            raise AuthenticationFailed()


class Logout(APIView):
    permission_classes = []

    def get(self, request, format=None):
        logout(request)
        return Response("Risk Managed API")


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = (permissions.IsAuthenticated, IsAdminOrReadOnly)
    filterset_class = OrganizationFilter


class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = (permissions.IsAuthenticated, IsAdminOrReadOnly)
    filterset_class = UniversityFilter


class NationalsViewSet(viewsets.ModelViewSet):
    queryset = Nationals.objects.all()
    serializer_class = NationalsSerializer
    permission_classes = (IsCreatingOrAuthenticated, IsNotAnAdministrator, IsAdminOrNoDelete)

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return self.queryset
        elif hasattr(user, "nationals"):
            return self.queryset.filter(user=user)
        elif hasattr(user, "host"):
            return self.queryset.filter(organization=user.host.organization)


class AdministratorViewSet(viewsets.ModelViewSet):
    queryset = Administrator.objects.all()
    serializer_class = AdministratorSerializer
    permission_classes = (IsCreatingOrAuthenticated, IsNotNationals, IsAdminOrNoDelete)

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return self.queryset
        elif hasattr(user, "administrator"):
            return self.queryset.filter(user=user)
        elif hasattr(user, "host"):
            return self.queryset.filter(university=user.host.university)


class HostViewSet(viewsets.ModelViewSet):
    queryset = Host.objects.all()
    serializer_class = HostSerializer
    permission_classes = (IsCreatingOrAuthenticated, IsAdminOrNoDelete)
    filterset_class = HostFilter

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return self.queryset
        elif hasattr(user, "host"):
            return self.queryset.filter(user=user)
        elif hasattr(user, "nationals"):
            return self.queryset.filter(nationals=user.nationals)
        elif hasattr(user, "administrator"):
            return self.queryset.filter(administrator=user.administrator)


class CarbonCopyAddressViewSet(viewsets.ModelViewSet):
    queryset = CarbonCopyAddress.objects.all()
    serializer_class = CarbonCopyAddressSerializer
    filterset_fields = ("id", "email")

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return self.queryset
        else:
            return self.queryset.filter(user=user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class IdentityViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    PaymentRequiredViewSet,
):

    queryset = Identity.objects.all()
    serializer_class = IdentitySerializer
    filterset_class = IdentityFilter

    def get_queryset(self):
        queryset = self.queryset

        # Custom `search` filter
        search = self.request.query_params.get("search", None)

        if search is None:
            return queryset

        search_list = search.split(" ")

        if len(search_list) == 1:
            queryset = queryset.filter(
                Q(first_name__icontains=search_list[0])
                | Q(last_name__icontains=search_list[0])
                | Q(gender=search_list[0])
            )
        elif len(search_list) == 2:
            queryset = queryset.filter(
                Q(first_name__icontains=search_list[0])
                | Q(last_name__icontains=search_list[0])
                | Q(gender=search_list[0]),
                Q(first_name__icontains=search_list[1])
                | Q(last_name__icontains=search_list[1])
                | Q(gender=search_list[1]),
            )

        elif len(search_list) == 3:
            queryset = queryset.filter(
                Q(first_name__icontains=search_list[0])
                | Q(last_name__icontains=search_list[0])
                | Q(gender=search_list[0]),
                Q(first_name__icontains=search_list[1])
                | Q(last_name__icontains=search_list[1])
                | Q(gender=search_list[1]),
                Q(first_name__icontains=search_list[2])
                | Q(last_name__icontains=search_list[2])
                | Q(gender=search_list[2]),
            )

        return queryset


class FlagViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    PaymentRequiredViewSet,
):
    queryset = Flag.objects.all()
    serializer_class = FlagSerializer
    filterset_class = FlagFilter

    def get_queryset(self):
        user = self.request.user
        queryset = None

        if user.is_superuser:
            queryset = self.queryset
        elif hasattr(user, "host"):
            queryset = self.queryset.filter(
                Q(host=user.host)
                | Q(nationals=user.host.nationals)
                | Q(administrator=user.host.administrator)
            )
        elif hasattr(user, "nationals"):
            queryset = self.queryset.filter(nationals=user.nationals)
        elif hasattr(user, "administrator"):
            queryset = self.queryset.filter(administrator=user.administrator)

        # Custom `search` filter
        search = self.request.query_params.get("search", None)

        if search is None:
            return queryset

        search_list = search.split(" ")

        if len(search_list) == 1:
            queryset = queryset.filter(
                Q(identity__first_name__icontains=search_list[0])
                | Q(identity__last_name__icontains=search_list[0])
                | Q(identity__gender=search_list[0])
            )
        elif len(search_list) == 2:
            queryset = queryset.filter(
                Q(identity__first_name__icontains=search_list[0])
                | Q(identity__last_name__icontains=search_list[0])
                | Q(identity__gender=search_list[0]),
                Q(identity__first_name__icontains=search_list[1])
                | Q(identity__last_name__icontains=search_list[1])
                | Q(identity__gender=search_list[1]),
            )

        elif len(search_list) == 3:
            queryset = queryset.filter(
                Q(identity__first_name__icontains=search_list[0])
                | Q(identity__last_name__icontains=search_list[0])
                | Q(identity__gender=search_list[0]),
                Q(identity__first_name__icontains=search_list[1])
                | Q(identity__last_name__icontains=search_list[1])
                | Q(identity__gender=search_list[1]),
                Q(identity__first_name__icontains=search_list[2])
                | Q(identity__last_name__icontains=search_list[2])
                | Q(identity__gender=search_list[2]),
            )

        return queryset

    def perform_create(self, serializer):
        user = self.request.user

        if hasattr(user, "nationals"):
            serializer.save(nationals=user.nationals, reach="Nationals")
        elif hasattr(user, "administrator"):
            serializer.save(administrator=user.administrator, reach="Administrator")
        elif hasattr(user, "host"):
            serializer.save(host=user.host, reach="Host")
        elif user.is_superuser:
            serializer.save(reach="Nationals")


class EventViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    PaymentRequiredViewSet,
):

    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = (permissions.IsAuthenticated, AdminsNationalsAdministratorsOnlyGet)
    filterset_class = EventFilter
    ordering = ("-date",)

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return self.queryset
        elif hasattr(user, "host"):
            return self.queryset.filter(host=user.host)
        elif hasattr(user, "nationals"):
            return self.queryset.filter(host__in=user.nationals.hosts.all())
        elif hasattr(user, "administrator"):
            return self.queryset.filter(host__in=user.administrator.hosts.all())

    def perform_create(self, serializer):
        serializer.save(host=self.request.user.host)

    @action(methods=["POST"], detail=True)
    def end(self, request, pk=None, *args, **kwargs):
        event = self.get_object()
        event.end_time = timezone.now()
        event.save()

        serializer = EventSerializer(event)

        return Response(serializer.data)


class ProcedureViewSet(mixins.RetrieveModelMixin, mixins.ListModelMixin, PaymentRequiredViewSet):
    queryset = Procedure.objects.all()
    serializer_class = ProcedureSerializer
    filterset_class = ProcedureFilter
    ordering = ("-completion_time",)

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser:
            return self.queryset
        elif hasattr(user, "host"):
            return self.queryset.filter(event__host=user.host)
        elif hasattr(user, "nationals"):
            hosts = user.nationals.hosts.all()
            return self.queryset.filter(event__host__in=hosts)
        elif hasattr(user, "administrator"):
            hosts = user.administrator.hosts.all()
            return self.queryset.filter(event__host__in=hosts)

    @action(methods=["POST"], detail=True)
    def complete(self, request, pk=None, *args, **kwargs):
        procedure = self.get_object()
        procedure.completion_time = timezone.now()
        procedure.save()

        serializer = ProcedureSerializer(procedure)

        return Response(serializer.data)


class InviteeViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    PaymentRequiredViewSet,
):
    queryset = Invitee.objects.all()
    serializer_class = InviteeSerializer
    permission_classes = (permissions.IsAuthenticated, NationalsAdministratorsReadOnly)
    filterset_class = InviteeFilter

    def get_queryset(self):
        user = self.request.user
        queryset = None

        if user.is_superuser:
            queryset = self.queryset
        elif hasattr(user, "host"):
            queryset = self.queryset.filter(event__host=user.host)
        elif hasattr(user, "nationals"):
            hosts = user.nationals.hosts.all()
            queryset = self.queryset.filter(event__host__in=hosts)
        elif hasattr(user, "administrator"):
            hosts = user.administrator.hosts.all()
            queryset = self.queryset.filter(event__host__in=hosts)

        # Custom `name` filter
        name = self.request.query_params.get("name", None)

        if name is None:
            return queryset

        name_list = name.split(" ")

        if len(name_list) == 1:
            queryset = queryset.filter(
                Q(first_name__icontains=name_list[0]) | Q(last_name__icontains=name_list[0])
            )
        elif len(name_list) == 2:
            queryset = queryset.filter(
                Q(first_name__icontains=name_list[0]) | Q(last_name__icontains=name_list[0]),
                Q(first_name__icontains=name_list[1]) | Q(last_name__icontains=name_list[1]),
            )

        return queryset


class GuestRegistrationViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    PaymentRequiredViewSet,
):

    queryset = GuestRegistration.objects.all()
    serializer_class = GuestRegistrationSerializer
    permission_classes = (permissions.IsAuthenticated, NationalsAdministratorsReadOnly)
    filterset_class = GuestRegistrationFilter
    ordering = ("-date_time_taken",)

    def get_queryset(self):
        user = self.request.user
        queryset = None

        if user.is_superuser:
            queryset = self.queryset
        elif hasattr(user, "host"):
            queryset = self.queryset.filter(event__host=user.host)
        elif hasattr(user, "nationals"):
            queryset = self.queryset.filter(event__host__in=user.nationals.hosts.all())
        elif hasattr(user, "administrator"):
            queryset = self.queryset.filter(event__host__in=user.administrator.hosts.all())

        # Custom `search` filter
        search = self.request.query_params.get("search", None)

        if search is None:
            pass
        else:
            search_list = search.split(" ")

            if len(search_list) == 1:
                queryset = queryset.filter(
                    Q(identity__first_name__icontains=search_list[0])
                    | Q(identity__last_name__icontains=search_list[0])
                    | Q(identity__gender=search_list[0])
                )
            elif len(search_list) == 2:
                queryset = queryset.filter(
                    Q(identity__first_name__icontains=search_list[0])
                    | Q(identity__last_name__icontains=search_list[0])
                    | Q(identity__gender=search_list[0]),
                    Q(identity__first_name__icontains=search_list[1])
                    | Q(identity__last_name__icontains=search_list[1])
                    | Q(identity__gender=search_list[1]),
                )

            elif len(search_list) == 3:
                queryset = queryset.filter(
                    Q(identity__first_name__icontains=search_list[0])
                    | Q(identity__last_name__icontains=search_list[0])
                    | Q(identity__gender=search_list[0]),
                    Q(identity__first_name__icontains=search_list[1])
                    | Q(identity__last_name__icontains=search_list[1])
                    | Q(identity__gender=search_list[1]),
                    Q(identity__first_name__icontains=search_list[2])
                    | Q(identity__last_name__icontains=search_list[2])
                    | Q(identity__gender=search_list[2]),
                )

        # Custom `unique` filter
        unique = self.request.query_params.get("unique", None)

        if unique is None:
            pass
        else:
            queryset = queryset.distinct(str(unique))

        return queryset
