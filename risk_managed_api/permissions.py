from rest_framework import permissions


class IsNotNationals(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return not hasattr(user, "nationals")


class IsNotAnAdministrator(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return not hasattr(user, "administrator")


class IsNotAnAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return not user.is_superuser


class IsCreatingOrAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return True

        if request.user.is_authenticated:
            return True

        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        if request.user.is_superuser:
            return True

        return False


class IsAdminOrNoDelete(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_anonymous:
            return True

        if request.method == "DELETE":
            return True if user.is_superuser else False

        return True


class AdminsNationalsAdministratorsOnlyGet(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if user.is_superuser or hasattr(user, "nationals") or hasattr(user, "administrator"):
            return request.method == "GET"

        return True


class NationalsAdministratorsReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if hasattr(user, "nationals") or hasattr(user, "administrator"):
            return request.method == "GET"

        return True
