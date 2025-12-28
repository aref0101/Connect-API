from rest_framework import permissions, status
from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth import get_user_model
User= get_user_model()


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner== request.user
    

class IsMeOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.username== request.user.username