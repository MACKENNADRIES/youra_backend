from rest_framework.permissions import BasePermission

class IsOwnerOrClaimant(BasePermission):
    """
    Custom permission to allow only the owner or the claimant of a RAK to update or delete it.
    """
    def has_object_permission(self, request, view, obj):
        # Allow if the user is either the owner or the claimant
        return obj.owner == request.user or (hasattr(obj, 'rak_claim') and obj.rak_claim.claimant == request.user)
