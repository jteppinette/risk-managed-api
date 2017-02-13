"""
This module defines the api app's custom permissions.
"""

from rest_framework import permissions


class IsNotNationals(permissions.BasePermission):
    """
    Return True if the user profile is not `Nationals`.
    """

    def has_permission(self, request, view):
        user = request.user
        return not hasattr(user, 'nationals')


class IsNotAnAdministrator(permissions.BasePermission):
    """
    Return True if the user profile is not an `Administrator`.
    """

    def has_permission(self, request, view):
        user = request.user
        return not hasattr(user, 'administrator')


class IsNotAnAdmin(permissions.BasePermission):
    """
    Return True if the user profile is not an `is_superuser`.
    """

    def has_permission(self, request, view):
        user = request.user
        return not user.is_superuser


class IsCreatingOrAuthenticated(permissions.BasePermission):
    """
    Return True if the user is doing a `POST` request or is authenticated.
    """

    def has_permission(self, request, view):
        if request.method == 'POST':
            return True

        if request.user.is_authenticated():
            return True

        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    If the request.method is not in `SAFE_METHODS`, then  return True only if
    the user `is_superuser`.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        if request.user.is_superuser:
            return True

        return False


class IsAdminOrNoDelete(permissions.BasePermission):
    """
    If the request.method is 'DELETE', then return True only if the user
    `is_superuser`.
    """

    def has_permission(self, request, view):
        user = request.user
        if user.is_anonymous():
            return True

        if request.method == 'DELETE':
            return True if user.is_superuser else False

        return True


class AdminsNationalsAdministratorsOnlyGet(permissions.BasePermission):
    """
    If user profile is an admin, `Administrator`, or `Nationals`, only `GET`.
    """

    def has_permission(self, request, view):
        user = request.user

        if user.is_superuser or hasattr(user, 'nationals') or hasattr(user, 'administrator'):
            return request.method == 'GET'

        return True

class NationalsAdministratorsReadOnly(permissions.BasePermission):
    """
    If user profile is `Nationals` or `Administrator`, only `GET`.
    """

    def has_permission(self, request, view):
        user = request.user

        if hasattr(user, 'nationals') or hasattr(user, 'administrator'):
            return request.method == 'GET'

        return True
