from rest_framework import permissions

from .models import Profile


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        profile = Profile.objects.get(user=user)

        if profile.role == "MA":
            return bool(request.user and request.user.is_authenticated)
