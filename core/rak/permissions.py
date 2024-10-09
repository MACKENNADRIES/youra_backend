from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a RandomActOfKindness to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS include GET, HEAD, OPTIONS (read-only methods)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only allow write access if the user is the owner or creator of the RAK
        return obj.owner == request.user or obj.creator == request.user


class IsClaimantOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow the claimant of a RAKClaim to edit or delete it.
    """
    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS include GET, HEAD, OPTIONS (read-only methods)
        if request.method in permissions.SAFE_METHODS:
            return True
        # Only allow write access if the user is the claimant of the RAKClaim
        return obj.claimant == request.user
