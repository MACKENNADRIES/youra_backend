from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import F, Q, Count
from rest_framework.views import APIView
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError, PermissionDenied

from .models import (
    RandomActOfKindness,
    Claimant,
    Collaborators,
    Notification,
    PayItForward,
)
from rak.serializers import (
    RandomActOfKindnessSerializer,
    ClaimantSerializer,
    CollaboratorsSerializer,
    NotificationSerializer,
    PayItForwardSerializer,
)
from users.models import UserProfile
from users.serializers import UserProfileSerializer, CustomUserSerializer

User = get_user_model()


# Create a RAK post (either offer or request)
class RandomActOfKindnessCreateView(APIView):
    """
    Create a new Random Act of Kindness (RAK) post.

    **Endpoint:** `/rak/`

    **Method:** `POST`

    **Permissions:** Authenticated users only.

    **Request Body:**
    - `title`: String, required.
    - `description`: String, required.
    - `media`: File, optional.
    - `private`: Boolean, optional.
    - `rak_type`: String, choices are defined in `POST_TYPE_CHOICES`.
    - `action`: String, required.
    - `aura_points_value`: Integer, optional.
    - `anonymous_rak`: Boolean, optional.
    - `allow_collaborators`: Boolean, optional.
    - `allow_claimants`: Boolean, optional.

    **Functionality:**
    - Creates a RAK post (offer or request).
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = RandomActOfKindnessSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(created_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Update a RAK post (edit an existing post)
class RandomActOfKindnessUpdateView(APIView):
    """
    Retrieve or update an existing RAK post.

    **Endpoint:** `/rak/<int:pk>/`

    **Methods:**
    - `GET`: Retrieve RAK details.
    - `PUT`: Update RAK details.
    - `PATCH`: Partially update RAK details.
    - `DELETE`: Delete the RAK post.

    **Permissions:** Authenticated users only. Only the creator can update or delete.

    **URL Parameters:**
    - `pk`: ID of the RAK post.

    **Functionality:**
    - Update a RAK post (edit an existing post).
    - Delete a RAK post.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, pk):
        return get_object_or_404(RandomActOfKindness, pk=pk)

    def get(self, request, pk):
        rak = self.get_object(pk)
        serializer = RandomActOfKindnessSerializer(rak)
        return Response(serializer.data)

    def put(self, request, pk):
        rak = self.get_object(pk)
        if rak.created_by != request.user:
            raise PermissionDenied("You cannot edit this RAK.")
        serializer = RandomActOfKindnessSerializer(rak, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        rak = self.get_object(pk)
        if rak.created_by != request.user:
            raise PermissionDenied("You cannot edit this RAK.")
        serializer = RandomActOfKindnessSerializer(rak, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        rak = self.get_object(pk)
        if rak.created_by != request.user:
            return Response(
                {"detail": "You cannot delete this RAK."},
                status=status.HTTP_403_FORBIDDEN,
            )
        rak.delete()
        return Response({"detail": "RAK deleted."}, status=status.HTTP_204_NO_CONTENT)


# Get all unclaimed RAK posts
class UnclaimedRAKListView(APIView):
    """
    List all unclaimed and public RAK posts.

    **Endpoint:** `/rak/unclaimed/`

    **Method:** `GET`

    **Permissions:** Allow any user.

    **Functionality:**
    - View all unclaimed RAK posts.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        raks = RandomActOfKindness.objects.filter(status="open", private=False)
        serializer = RandomActOfKindnessSerializer(raks, many=True)
        return Response(serializer.data)


#View all claimed RAK posts
class ClaimedRAKListView(APIView):
    """
    List all claimed and public RAK posts.

    **Endpoint:** `/rak/claimed/`

    **Method:** `GET`

    **Permissions:** Allow any user.

    **Functionality:**
    - View all claimed RAK posts.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        raks = RandomActOfKindness.objects.filter(
            status="in progress", private=False, claims__isnull=False
        ).distinct()
        serializer = RandomActOfKindnessSerializer(raks, many=True)
        return Response(serializer.data)


# Claim a RAK post –  this will automatically update status to 'in progress.'
class RAKClaimView(APIView):
    """
    Claim a RAK post, automatically updating its status to 'in progress.'

    **Endpoint:** `/rak/<int:pk>/claim/`

    **Method:** `POST`

    **Permissions:** Authenticated users only.

    **URL Parameters:**
    - `pk`: ID of the RAK post to claim.

    **Request Body:**
    - `anonymous_claimant`: Boolean, optional.
    - `comment`: String, optional.

    **Functionality:**
    - Claim a RAK post – automatically updates to 'in progress.'
    - Allow users to claim RAKs anonymously.
    """

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


# Collaborate on a RAK post
class RAKCollaborateView(APIView):
    """
    Collaborate on a RAK post.

    **Endpoint:** `/rak/<int:pk>/collaborate/`

    **Method:** `POST`

    **Permissions:** Authenticated users only.

    **URL Parameters:**
    - `pk`: ID of the RAK post to collaborate on.

    **Request Body:**
    - `anonymous_collaborator`: Boolean, optional.
    - `comment`: String, optional.

    **Functionality:**
    - Collaborate on a RAK post.
    - Allow users to collaborate on RAKs anonymously.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        rak = get_object_or_404(RandomActOfKindness, pk=pk)
        anonymous = request.data.get("anonymous_collaborator", False)
        comment = request.data.get("comment", "")
        try:
            rak.collaborate(
                request.user, comment=comment, anonymous_collaborator=anonymous
            )
            return Response(
                {"detail": "Collaboration started successfully."},
                status=status.HTTP_200_OK,
            )
        except ValueError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Enable collaborators on a RAK
class EnableCollaboratorsView(APIView):
    """
    Enable collaborators on a RAK post, allowing multiple collaborators.

    **Endpoint:** `/rak/<int:pk>/enable-collaborators/`

    **Method:** `POST`

    **Permissions:** Authenticated users only. Only the creator can enable collaborators.

    **URL Parameters:**
    - `pk`: ID of the RAK post.

    **Functionality:**
    - Enable collaboration on a RAK post.
    """

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


# Change the status of a RAK post
class RAKStatusUpdateView(APIView):
    """
    Update the status of a RAK post.

    **Endpoint:** `/rak/<int:pk>/status/`

    **Method:** `POST`

    **Permissions:** Authenticated users only. Only the creator can change the status.

    **URL Parameters:**
    - `pk`: ID of the RAK post.

    **Request Body:**
    - `status`: String, required. Must be one of ['open', 'in progress', 'completed'].

    **Functionality:**
    - Change the status of a RAK post.
    - Award aura points to the claimant(s) and collaborators once the RAK is completed.
    """

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


# Create a Pay It Forward instance
class CreatePayItForwardView(APIView):
    """
    Create a Pay It Forward, generating a new RAK post linked to an original RAK.

    **Endpoint:** `/rak/<int:pk>/pay-it-forward/`

    **Method:** `POST`

    **Permissions:** Authenticated users only.

    **URL Parameters:**
    - `pk`: ID of the original completed RAK post.

    **Request Body:**
    - Fields required to create a new RAK post.

    **Functionality:**
    - Once a RAK is completed, if the Pay It Forward feature is enabled, forwards are displayed in the feed.
    - Pay It Forward can be claimed and turns into a new RAK post.
    """

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
        serializer = RandomActOfKindnessSerializer(data=data)
        if serializer.is_valid():
            new_rak = serializer.save(created_by=request.user)
            # Create PayItForward instance
            PayItForward.objects.create(original_rak=original_rak, new_rak=new_rak)
            return Response(
                {"detail": "Pay It Forward created.", "new_rak_id": new_rak.id},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# Fetch all RAK claims
class AllClaimsView(APIView):
    """
    List all RAK claims.

    **Endpoint:** `/claims/`

    **Method:** `GET`

    **Permissions:** Authenticated users only.

    **Functionality:**
    - Fetch all RAK claims.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        claims = Claimant.objects.all()
        serializer = ClaimantSerializer(claims, many=True)
        return Response(serializer.data)


# Fetch all claimants for a RAK
class RAKClaimantsView(APIView):
    """
    List all claimants for a specific RAK.

    **Endpoint:** `/rak/<int:pk>/claimants/`

    **Method:** `GET`

    **Permissions:** Authenticated users only.

    **URL Parameters:**
    - `pk`: ID of the RAK post.

    **Functionality:**
    - Fetch all claimants.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        rak = get_object_or_404(RandomActOfKindness, pk=pk)
        claimants = rak.claims.all()
        serializer = ClaimantSerializer(claimants, many=True)
        return Response(serializer.data)


# Fetch all collaborators for a RAK
class RAKCollaboratorsView(APIView):
    """
    List all collaborators for a specific RAK.

    **Endpoint:** `/rak/<int:pk>/collaborators/`

    **Method:** `GET`

    **Permissions:** Authenticated users only.

    **URL Parameters:**
    - `pk`: ID of the RAK post.

    **Functionality:**
    - Fetch all collaborators.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        rak = get_object_or_404(RandomActOfKindness, pk=pk)
        collaborators = rak.collabs.all()
        serializer = CollaboratorsSerializer(collaborators, many=True)
        return Response(serializer.data)


# Fetch user details
class UserDetailView(APIView):
    """
    Retrieve user details.

    **Endpoint:** `/users/<int:pk>/`

    **Method:** `GET`

    **Permissions:** Authenticated users only.

    **URL Parameters:**
    - `pk`: ID of the user.

    **Functionality:**
    - Fetch user details.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data)


# Display a user’s aura points, percentages and levels
class UserAuraPointsView(APIView):
    """
    Display a user's aura points and percentage towards the next level.

    **Endpoint:** `/users/<int:pk>/aura-points/`

    **Method:** `GET`

    **Permissions:** Authenticated users only.

    **URL Parameters:**
    - `pk`: ID of the user.

    **Functionality:**
    - Display a user’s aura points and percentages towards levels.
    - Display how a user’s aura points are calculated.
    """

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
class AuraPointsLeaderboardView(APIView):
    """
    Display a leaderboard of users based on aura points.

    **Endpoint:** `/leaderboard/`

    **Method:** `GET`

    **Permissions:** Allow any user.

    **Functionality:**
    - Display a leaderboard of users based on aura points.
    - Assign colors to different aura levels (handled in serializers or frontend).
    - Award badges based on aura levels, displayed on the profile.
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user_profiles = UserProfile.objects.order_by("-aura_points")[:10]
        serializer = UserProfileSerializer(user_profiles, many=True)
        return Response(serializer.data)


# Follow a user
class FollowUserView(APIView):
    """
    Follow a user.

    **Endpoint:** `/users/<int:pk>/follow/`

    **Method:** `POST`

    **Permissions:** Authenticated users only.

    **URL Parameters:**
    - `pk`: ID of the user to follow.

    **Functionality:**
    - Follow users.
    """

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


# Unfollow a user
class UnfollowUserView(APIView):
    """
    Unfollow a user.

    **Endpoint:** `/users/<int:pk>/unfollow/`

    **Method:** `POST`

    **Permissions:** Authenticated users only.

    **URL Parameters:**
    - `pk`: ID of the user to unfollow.

    **Functionality:**
    - Unfollow users.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        target_user = get_object_or_404(User, pk=pk)
        request.user.userprofile.following.remove(target_user.userprofile)
        return Response({"detail": "User unfollowed."}, status=status.HTTP_200_OK)


# Block users
class BlockUserView(APIView):
    """
    Block a user.

    **Endpoint:** `/users/<int:pk>/block/`

    **Method:** `POST`

    **Permissions:** Authenticated users only.

    **URL Parameters:**
    - `pk`: ID of the user to block.

    **Functionality:**
    - Block users.
    """

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
class ReportUserView(APIView):
    """
    Report a user for inappropriate behavior.

    **Endpoint:** `/users/<int:pk>/report/`

    **Method:** `POST`

    **Permissions:** Authenticated users only.

    **URL Parameters:**
    - `pk`: ID of the user to report.

    **Functionality:**
    - Report users.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        target_user = get_object_or_404(User, pk=pk)
        # Implement reporting logic here, e.g., create a Report model instance
        return Response({"detail": "User reported."}, status=status.HTTP_200_OK)


# Display a curated feed of followed users
class UserFeedView(APIView):
    """
    Display a curated feed of RAKs from users the current user follows.

    **Endpoint:** `/feed/`

    **Method:** `GET`

    **Permissions:** Authenticated users only.

    **Functionality:**
    - Display a curated feed of followed users.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        following_users = user.userprofile.following.values_list("user", flat=True)
        raks = RandomActOfKindness.objects.filter(
            created_by__in=following_users
        ).exclude(private=True)
        serializer = RandomActOfKindnessSerializer(raks, many=True)
        return Response(serializer.data)


# Explore page: View RAKs from people I don't follow
class ExploreRAKView(APIView):
    """
    Display RAKs from users the current user does not follow.

    **Endpoint:** `/explore/`

    **Method:** `GET`

    **Permissions:** Authenticated users only.

    **Functionality:**
    - View an explore page with RAKs from people the user doesn’t follow.
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        following_users = user.userprofile.following.values_list("user", flat=True)
        raks = (
            RandomActOfKindness.objects.exclude(created_by__in=following_users)
            .exclude(created_by=user)
            .exclude(private=True)
        )
        serializer = RandomActOfKindnessSerializer(raks, many=True)
        return Response(serializer.data)


# Display how a user’s aura points are calculated
class UserAuraPointsDetailsView(APIView):
    """
    Display details on how a user's aura points are calculated.

    **Endpoint:** `/users/<int:pk>/aura-points-details/`

    **Method:** `GET`

    **Permissions:** Authenticated users only.

    **URL Parameters:**
    - `pk`: ID of the user.

    **Functionality:**
    - Display how a user’s aura points are calculated (RAKs, Pay It Forwards, etc.).
    """

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
class UserProfileUpdateView(APIView):
    """
    Retrieve or update the user's profile details.

    **Endpoint:** `/user/profile/`

    **Methods:**
    - `GET`: Retrieve profile details.
    - `PUT`: Update profile details.
    - `PATCH`: Partially update profile details.

    **Permissions:** Authenticated users only.

    **Functionality:**
    - Add profile details: profile picture, bio, etc.
    - Allow users to create and manage posts (handled elsewhere).
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        profile = request.user.userprofile
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request):
        profile = request.user.userprofile
        serializer = UserProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        profile = request.user.userprofile
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Delete a user
class UserDeleteView(APIView):
    """
    Deactivate the user's account.

    **Endpoint:** `/user/delete/`

    **Method:** `DELETE`

    **Permissions:** Authenticated users only.

    **Functionality:**
    - Delete a user (deactivate account).
    """

    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save()
        return Response(
            {"detail": "User account deactivated."}, status=status.HTTP_204_NO_CONTENT
        )
