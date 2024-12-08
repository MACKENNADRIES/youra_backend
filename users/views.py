from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from users.models import UserProfile, CustomUser, Follow
from users.serializers import (
    CustomUserSerializer,
    UserProfileSerializer,
    FollowSerializer,
    CustomAuthTokenSerializer,
)


class UserProfileImageUploadView(APIView):
    """
    View to upload or update a user's profile image.
    """

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request):
        """
        Handle image upload for the authenticated user.

        Args:
            request: The HTTP request containing the image file.

        Returns:
            Response: A DRF Response object with the updated profile data.
        """
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile does not exist."}, status=404)

        serializer = UserProfileSerializer(
            user_profile, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)


class CustomAuthToken(ObtainAuthToken):
    """
    Custom authentication token view that returns a token along with user information.

    This view extends the default `ObtainAuthToken` to include the user's ID and username
    in the response upon successful authentication.
    """

    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to authenticate a user and return a token.

        Args:
            request: The HTTP request containing the user's credentials.

        Returns:
            Response: A DRF Response object containing the authentication token,
                    user ID, and username.

        Raises:
            ValidationError: If the provided credentials are invalid.
        """
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user_id": user.pk, "username": user.username}
        )


class CustomUserList(APIView):
    """
    View to list all users or create a new user.

    Allows anyone to view the list of users or register a new user.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        """
        Retrieve a list of all users.

        Args:
            request: The HTTP request.

        Returns:
            Response: A DRF Response object containing serialized user data.
        """
        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Create a new user.

        Args:
            request: The HTTP request containing user data.

        Returns:
            Response: A DRF Response object containing serialized user data and HTTP status code.

        Raises:
            ValidationError: If the provided data is invalid.
        """
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class CustomUserDetail(APIView):
    """
    View to retrieve, update, or delete a CustomUser instance.

    Only authenticated users can perform these actions.
    """

    def get_object(self, pk):
        """
        Retrieve a CustomUser instance by primary key.

        Args:
            pk (int): The primary key of the user.

        Returns:
            CustomUser: The user instance.

        Raises:
            Http404: If the user does not exist.
        """
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404("User not found")

    def get(self, request, pk):
        """
        Retrieve a user by ID.

        Args:
            request: The HTTP request.
            pk (int): The primary key of the user.

        Returns:
            Response: A DRF Response object containing serialized user data.
        """
        user = self.get_object(pk)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=200)

    def put(self, request, pk):
        """
        Update a user by ID.

        Args:
            request: The HTTP request containing updated user data.
            pk (int): The primary key of the user.

        Returns:
            Response: A DRF Response object containing serialized user data.

        Raises:
            ValidationError: If the provided data is invalid.
        """
        user = self.get_object(pk)
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        """
        Delete a user by ID.

        Args:
            request: The HTTP request.
            pk (int): The primary key of the user.

        Returns:
            Response: A DRF Response object indicating success.
        """
        user = self.get_object(pk)
        user.delete()
        return Response({"message": "User deleted successfully"}, status=204)


class UserProfileView(APIView):
    """
    View to retrieve the authenticated user's profile.

    Only authenticated users can access their own profile.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retrieve the authenticated user's profile.

        Args:
            request: The HTTP request.

        Returns:
            Response: A DRF Response object containing serialized user profile data.
        """
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile does not exist."}, status=404)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=200)


class UserProfileDetailView(APIView):
    """
    View to retrieve a user's profile by user ID.

    Only authenticated users can access this view.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        """
        Retrieve a user's profile by user ID.

        Args:
            request: The HTTP request.
            user_id (int): The ID of the user whose profile is to be retrieved.

        Returns:
            Response: A DRF Response object containing serialized user profile data.
        """
        try:
            user_profile = UserProfile.objects.get(user_id=user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile does not exist."}, status=404)

        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=200)


class LeaderboardView(APIView):
    """
    View to display a leaderboard of top users based on aura points.

    Allows anyone to view the top 10 users.
    """

    def get(self, request):
        """
        Retrieve the top 10 users ordered by aura points.

        Args:
            request: The HTTP request.

        Returns:
            Response: A DRF Response object containing a list of top users.
        """
        top_users = UserProfile.objects.order_by("-aura_points")
        data = [
            {
                "username": user.user.username,
                "aura_points": user.aura_points,
                "aura_level": user.aura_level,
                "aura_sub_level": user.aura_sub_level,
            }
            for user in top_users
        ]
        return Response(data, status=200)


class FollowUserView(APIView):
    """
    View to follow a user.

    Only authenticated users can follow other users.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        """
        Follow a user by their user ID.

        Args:
            request: The HTTP request.
            user_id (int): The ID of the user to follow.

        Returns:
            Response: A DRF Response object indicating the result.
        """
        followed_user = CustomUser.objects.get(id=user_id)
        follow, created = Follow.objects.get_or_create(
            follower=request.user, followed=followed_user
        )
        if not created:
            return Response(
                {"message": "You are already following this user."}, status=400
            )
        return Response({"message": "You are now following this user."}, status=201)


class UnfollowUserView(APIView):
    """
    View to unfollow a user.

    Only authenticated users can unfollow other users.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        """
        Unfollow a user by their user ID.

        Args:
            request: The HTTP request.
            user_id (int): The ID of the user to unfollow.

        Returns:
            Response: A DRF Response object indicating the result.
        """
        followed_user = CustomUser.objects.get(id=user_id)
        try:
            follow = Follow.objects.get(follower=request.user, followed=followed_user)
            follow.delete()
            return Response({"message": "You have unfollowed this user."}, status=204)
        except Follow.DoesNotExist:
            return Response({"error": "You are not following this user."}, status=400)


class FollowersListView(APIView):
    """
    View to list all followers of a user.

    Only authenticated users can access this view.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        """
        Retrieve a list of followers for a user.

        Args:
            request: The HTTP request.
            user_id (int): The ID of the user whose followers are to be retrieved.

        Returns:
            Response: A DRF Response object containing serialized follower data.
        """
        user = CustomUser.objects.get(id=user_id)
        followers = user.followers.all()  # All users following this user
        serializer = FollowSerializer(followers, many=True)
        return Response(serializer.data)


class FollowingListView(APIView):
    """
    View to list all users that a user is following.

    Only authenticated users can access this view.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        """
        Retrieve a list of users that a user is following.

        Args:
            request: The HTTP request.
            user_id (int): The ID of the user whose following list is to be retrieved.

        Returns:
            Response: A DRF Response object containing serialized data.
        """
        user = CustomUser.objects.get(id=user_id)
        following = user.following.all()  # All users this user is following
        serializer = FollowSerializer(following, many=True)
        return Response(serializer.data)
