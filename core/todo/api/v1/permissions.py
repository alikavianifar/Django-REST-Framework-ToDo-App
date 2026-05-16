from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Only the task owner may access or modify the object."""

    def has_object_permission(self, request, view, obj):
        return obj.author.user == request.user
