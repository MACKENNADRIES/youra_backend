from rest_framework import permissions

class IsOwnerOrClaimant(permissions.BasePermission):
    """
    Custom permission to allow the owner or claimant to modify RAKs.
    """
    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS (GET, HEAD, OPTIONS) allow read-only access to all users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Allow write access if the user is the owner or the claimant (if applicable)
        return obj.owner == request.user or getattr(obj, 'rak_claim', None) and obj.rak_claim.claimant == request.user
