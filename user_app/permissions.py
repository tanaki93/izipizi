from rest_framework import permissions

from .models import Admin,Operator, Client


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous():
            return False
        return request.user.user_type == Admin


class IsOperator(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous():
            return False
        return request.user.user_type == Operator


class IsClient(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_anonymous():
            return False
        return request.user.user_type == Client

