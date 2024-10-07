from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a RAKPost to edit or delete it.
    """

    def has_object_permission(self, request, view, obj):
        # SAFE_METHODS include GET, HEAD, and OPTIONS (read-only methods)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only allow write access if the user is the owner of the RAKPost
        return obj.owner == request.user
