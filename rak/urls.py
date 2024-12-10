from django.urls import path
from . import views

urlpatterns = [
    # RAK posts
    path("rak/", views.RandomActOfKindnessCreateView.as_view(), name="rak-create"),
    path("all/", views.AllRAKListView.as_view(), name="rak-all"),
    path(
        "rak/<int:pk>/",
        views.RandomActOfKindnessUpdateView.as_view(),
        name="rak-update",
    ),
    # path("rak/<int:pk>/delete/", views.RAKDeleteView.as_view(), name="rak-delete"),
    path("rak/unclaimed/", views.UnclaimedRAKListView.as_view(), name="rak-unclaimed"),
    path("rak/claimed/", views.ClaimedRAKListView.as_view(), name="rak-claimed"),
    path("rak/<int:pk>/claim/", views.RAKClaimView.as_view(), name="rak-claim"),
    path(
        "rak/<int:pk>/collaborators/",
        views.RAKCollaboratorsView.as_view(),
        name="rak-collaborators",
    ),
    path(
        "rak/<int:pk>/collaborate/",
        views.RAKCollaborateView.as_view(),
        name="rak-collaborate",
    ),
    path(
        "my-claimed-raks/", views.MyClaimedRAKListView.as_view(), name="my-claimed-raks"
    ),
    path("my-posted-raks/", views.MyPostedRAKListView.as_view(), name="my-posted-raks"),
    path(
        "rak/<int:pk>/enable-collaborators/",
        views.EnableCollaboratorsView.as_view(),
        name="rak-enable-collaborators",
    ),
    path(
        "rak/<int:pk>/status/",
        views.RAKStatusUpdateView.as_view(),
        name="rak-status-update",
    ),
    path(
        "rak/<int:pk>/pay-it-forward/",
        views.CreatePayItForwardView.as_view(),
        name="create-pay-it-forward",
    ),
    path(
        "rak/<int:pk>/claimants/",
        views.RAKClaimantsView.as_view(),
        name="rak-claimants",
    ),
    # Claims
    path("claims/", views.AllClaimsView.as_view(), name="all-claims"),
    # User profiles --- move ????????????????????????????
    path("users/<int:pk>/", views.UserDetailView.as_view(), name="user-detail"),
    path(
        "users/<int:pk>/aura-points/",
        views.UserAuraPointsView.as_view(),
        name="user-aura-points",
    ),
    path(
        "users/<int:pk>/aura-points-details/",
        views.UserAuraPointsDetailsView.as_view(),
        name="user-aura-points-details",
    ),
    path(
        "user/profile/",
        views.UserProfileUpdateView.as_view(),
        name="user-profile-update",
    ),
    path("user/delete/", views.UserDeleteView.as_view(), name="user-delete"),
    # Social actions
    path("users/<int:pk>/follow/", views.FollowUserView.as_view(), name="user-follow"),
    path(
        "users/<int:pk>/unfollow/",
        views.UnfollowUserView.as_view(),
        name="user-unfollow",
    ),
    path("users/<int:pk>/block/", views.BlockUserView.as_view(), name="user-block"),
    path("users/<int:pk>/report/", views.ReportUserView.as_view(), name="user-report"),
    # Feeds
    path("feed/", views.UserFeedView.as_view(), name="user-feed"),
    path("explore/", views.ExploreRAKView.as_view(), name="explore"),
    # Leaderboard
    path("leaderboard/", views.AuraPointsLeaderboardView.as_view(), name="leaderboard"),
]
