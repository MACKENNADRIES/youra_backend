# rak/permissions.py

from rest_framework import permissions

class IsOwnerOrClaimant(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object or claimants to access it.
    """

    def has_object_permission(self, request, view, obj):
        # Permissions are only allowed to the owner or claimant of the RAK
        return obj.creator == request.user or obj.claimant == request.user
