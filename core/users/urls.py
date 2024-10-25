from django.urls import path
from .views import (
    CustomUserList,
    CustomUserDetail,
    FollowingListView,
    UserProfileView,
    FollowUserView,
    FollowersListView,
    UnfollowUserView,
    LeaderboardView,
    CustomAuthToken,
    UserProfileDetailView,
)

urlpatterns = [
    # User-related endpoints
    path("", CustomUserList.as_view(), name="user-list"),  # List and create users
    path(
        "<int:pk>/", CustomUserDetail.as_view(), name="user-detail"
    ),  # Detail, update, delete specific users
    # User profile view
    path(
        "profile/", UserProfileView.as_view(), name="user-profile"
    ),  # View and update logged-in user's profile
    path(
        "profile/<int:user_id>/",
        UserProfileDetailView.as_view(),
        name="user-profile-detail",
    ),
    # Leaderboard
    path(
        "leaderboard/", LeaderboardView.as_view(), name="leaderboard"
    ),  # Display top users by aura points
    # Token-based authentication
    path(
        "token/", CustomAuthToken.as_view(), name="custom-token-auth"
    ),  # Custom token authentication without 'api/'
    path("follow/<int:user_id>/", FollowUserView.as_view(), name="follow-user"),
    path("unfollow/<int:user_id>/", UnfollowUserView.as_view(), name="unfollow-user"),
    path(
        "followers/<int:user_id>/", FollowersListView.as_view(), name="followers-list"
    ),
    path(
        "following/<int:user_id>/", FollowingListView.as_view(), name="following-list"
    ),
]
