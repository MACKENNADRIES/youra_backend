from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import F, Q, Count
from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import (
    RandomActOfKindness,
    Claimant,
    Notification,
    PayItForward,
    # Ensure you have UserProfile model
    # UserProfile,
)
from rak.serializers import (
    RandomActOfKindnessSerializer,
    ClaimantSerializer,
    NotificationSerializer,
    PayItForwardSerializer,
)
from users.serializers import UserProfileSerializer, CustomUserSerializer

User = get_user_model()


# 1. Create a RAK post (offer or request)
class RandomActOfKindnessCreateView(generics.CreateAPIView):
    queryset = RandomActOfKindness.objects.all()
    serializer_class = RandomActOfKindnessSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


# 2. Update a RAK post (edit an existing post)
class RandomActOfKindnessUpdateView(generics.RetrieveUpdateAPIView):
    queryset = RandomActOfKindness.objects.all()
    serializer_class = RandomActOfKindnessSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_update(self, serializer):
        rak = serializer.instance
        if rak.created_by != self.request.user:
            raise PermissionDenied("You cannot edit this RAK.")
        serializer.save()


# 3. View all unclaimed RAK posts
class UnclaimedRAKListView(generics.ListAPIView):
    serializer_class = RandomActOfKindnessSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return RandomActOfKindness.objects.filter(status="open", private=False)


# 4. Claim a RAK post – automatically update to 'in progress.'
class RAKClaimView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        rak = get_object_or_404(RandomActOfKindness, pk=pk)
        anonymous = request.data.get("anonymous_claimant", False)
        comment = request.data.get("comment", "")
        try:
            rak.claim_rak(request.user, comment=comment, anonymous_claimant=anonymous)
            return Response(
                {"detail": "RAK claimed successfully."}, status=status.HTTP_200_OK
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 5. Enable collaborators on a RAK
class EnableCollaboratorsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        rak = get_object_or_404(RandomActOfKindness, pk=pk)
        if rak.created_by != request.user:
            return Response(
                {"detail": "You cannot modify this RAK."},
                status=status.HTTP_403_FORBIDDEN,
            )
        rak.enable_collaborators()
        return Response(
            {"detail": "Collaborators enabled for this RAK."}, status=status.HTTP_200_OK
        )


# 6. Change the status of a RAK post
class RAKStatusUpdateView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        rak = get_object_or_404(RandomActOfKindness, pk=pk)
        if rak.created_by != request.user:
            return Response(
                {"detail": "You cannot change the status of this RAK."},
                status=status.HTTP_403_FORBIDDEN,
            )
        new_status = request.data.get("status")
        if new_status not in ["open", "in progress", "completed"]:
            return Response(
                {"detail": "Invalid status."}, status=status.HTTP_400_BAD_REQUEST
            )
        if new_status == "completed":
            rak.complete_rak()
        else:
            rak.status = new_status
            rak.save()
        return Response({"detail": "RAK status updated."}, status=status.HTTP_200_OK)


# 7 & 8. Award aura points to claimants once RAK is completed
# This is handled in the `complete_rak` method of the `RandomActOfKindness` model.


# 9. Create Pay It Forward
class CreatePayItForwardView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        original_rak = get_object_or_404(RandomActOfKindness, pk=pk)
        if original_rak.status != "completed":
            return Response(
                {"detail": "RAK must be completed to pay it forward."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        # Create a new RAK
        data = request.data.copy()
        data["created_by"] = request.user.id
        serializer = RandomActOfKindnessSerializer(data=data)
        if serializer.is_valid():
            new_rak = serializer.save()
            # Create PayItForward instance
            PayItForward.objects.create(original_rak=original_rak, new_rak=new_rak)
            return Response(
                {"detail": "Pay It Forward created.", "new_rak_id": new_rak.id},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 10. Pay It Forward can be claimed and turns into a new RAK post
# This is handled in the `CreatePayItForwardView`.

# Additional functionalities:


# Fetch all RAK claims
class AllClaimsView(generics.ListAPIView):
    serializer_class = ClaimantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Claimant.objects.all()


# Fetch all claimants/collaborators for a RAK
class RAKClaimantsView(generics.ListAPIView):
    serializer_class = ClaimantSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        rak_id = self.kwargs["pk"]
        rak = get_object_or_404(RandomActOfKindness, pk=rak_id)
        return rak.claims.all()


# Fetch user details
class UserDetailView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer  # Ensure you have this serializer
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]


# Display a user’s aura points and percentages towards levels
class UserAuraPointsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        profile = user.userprofile
        data = {
            "aura_points": profile.aura_points,
            "level": profile.level,
            "percentage_to_next_level": profile.percentage_to_next_level(),
        }
        return Response(data)


# Display a leaderboard of users based on aura points
class AuraPointsLeaderboardView(generics.ListAPIView):
    serializer_class = UserProfileSerializer  # Ensure you have this serializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return UserProfile.objects.order_by("-aura_points")[:10]


# Follow/unfollow users
class FollowUserView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        target_user = get_object_or_404(User, pk=pk)
        if target_user == request.user:
            return Response(
                {"detail": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.userprofile.following.add(target_user.userprofile)
        return Response({"detail": "User followed."}, status=status.HTTP_200_OK)


class UnfollowUserView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        target_user = get_object_or_404(User, pk=pk)
        request.user.userprofile.following.remove(target_user.userprofile)
        return Response({"detail": "User unfollowed."}, status=status.HTTP_200_OK)


# Block users
class BlockUserView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        target_user = get_object_or_404(User, pk=pk)
        if target_user == request.user:
            return Response(
                {"detail": "You cannot block yourself."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.userprofile.blocked_users.add(target_user.userprofile)
        return Response({"detail": "User blocked."}, status=status.HTTP_200_OK)


# Report users
class ReportUserView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        target_user = get_object_or_404(User, pk=pk)
        # Implement reporting logic here, e.g., create a Report model instance
        return Response({"detail": "User reported."}, status=status.HTTP_200_OK)


# Display a curated feed of followed users
class UserFeedView(generics.ListAPIView):
    serializer_class = RandomActOfKindnessSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        following_users = user.userprofile.following.values_list("user", flat=True)
        return RandomActOfKindness.objects.filter(
            created_by__in=following_users
        ).exclude(private=True)


# Explore page: View RAKs from people I don't follow
class ExploreRAKView(generics.ListAPIView):
    serializer_class = RandomActOfKindnessSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        following_users = user.userprofile.following.values_list("user", flat=True)
        return (
            RandomActOfKindness.objects.exclude(created_by__in=following_users)
            .exclude(created_by=user)
            .exclude(private=True)
        )


# Display how a user’s aura points are calculated
class UserAuraPointsDetailsView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        profile = user.userprofile
        data = {
            "aura_points": profile.aura_points,
            "from_raks": profile.aura_points_from_raks(),
            "from_pay_it_forward": profile.aura_points_from_pay_it_forward(),
            # Add other sources if necessary
        }
        return Response(data)


# Add profile details: profile picture, bio, etc.
class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer  # Ensure you have this serializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.userprofile


# Delete a user
class UserDeleteView(views.APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save()
        return Response(
            {"detail": "User account deactivated."}, status=status.HTTP_204_NO_CONTENT
        )


# Delete a RAK post
class RAKDeleteView(generics.DestroyAPIView):
    queryset = RandomActOfKindness.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        rak = get_object_or_404(RandomActOfKindness, pk=pk)
        if rak.created_by != request.user:
            return Response(
                {"detail": "You cannot delete this RAK."},
                status=status.HTTP_403_FORBIDDEN,
            )
        rak.delete()
        return Response({"detail": "RAK deleted."}, status=status.HTTP_204_NO_CONTENT)
