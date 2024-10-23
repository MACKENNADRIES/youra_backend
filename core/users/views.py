from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from users.models import UserProfile, CustomUser, Follow
from users.serializers import (
    CustomUserSerializer,
    UserProfileSerializer,
    FollowSerializer,
    CustomAuthTokenSerializer,
)


class CustomAuthToken(ObtainAuthToken):
    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
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
    permission_classes = [AllowAny]

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class CustomUserDetail(APIView):
    """
    Retrieve, update, or delete a CustomUser instance.
    """

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404("User not found")

    def get(self, request, pk):
        user = self.get_object(pk)
        serializer = CustomUserSerializer(user)
        return Response(serializer.data, status=200)

    def put(self, request, pk):
        user = self.get_object(pk)
        serializer = CustomUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=200)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        user = self.get_object(pk)
        user.delete()
        return Response({"message": "User deleted successfully"}, status=204)


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile does not exist."}, status=404)
        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=200)


class UserProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]  # Make sure the request is authenticated

    def get(self, request, user_id):
        try:
            user_profile = UserProfile.objects.get(
                user_id=user_id
            )  # Fetch profile by user_id
        except UserProfile.DoesNotExist:
            return Response({"error": "UserProfile does not exist."}, status=404)

        serializer = UserProfileSerializer(user_profile)
        return Response(serializer.data, status=200)


class LeaderboardView(APIView):
    def get(self, request):
        top_users = UserProfile.objects.order_by("-aura_points")[:10]
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
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
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
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        followed_user = CustomUser.objects.get(id=user_id)
        try:
            follow = Follow.objects.get(follower=request.user, followed=followed_user)
            follow.delete()
            return Response({"message": "You have unfollowed this user."}, status=204)
        except Follow.DoesNotExist:
            return Response({"error": "You are not following this user."}, status=400)


class FollowersListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = CustomUser.objects.get(id=user_id)
        followers = user.followers.all()  # All users following this user
        serializer = FollowSerializer(followers, many=True)
        return Response(serializer.data)


class FollowingListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        user = CustomUser.objects.get(id=user_id)
        following = user.following.all()  # All users this user is following
        serializer = FollowSerializer(following, many=True)
        return Response(serializer.data)
