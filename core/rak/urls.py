from django.urls import path
from .views import (
    RandomActOfKindnessList,
    RandomActOfKindnessDetail,
    # RAKClaimList,
    # RAKClaimDetail,
    PayItForwardView,
    EnableCollaborationView,
    JoinRAKView,
    PayItForwardListCreateView,
    PayItForwardDetailView,
)

urlpatterns = [
    # RAK-related endpoints
    path(
        "rakposts/", RandomActOfKindnessList.as_view(), name="rakpost-list"
    ),  # List and create RAK posts
    path(
        "rakposts/<int:pk>/", RandomActOfKindnessDetail.as_view(), name="rakpost-detail"
    ),  # Retrieve, update, delete RAK posts
    # Claim-related endpoints
    # path(
    #     "claimedraks/", RAKClaimList.as_view(), name="rakclaim-list"
    # ),  # List and create RAK claims
    # path(
    #     "rakclaims/<int:pk>/", RAKClaimDetail.as_view(), name="rakclaim-detail"
    # ),  # Retrieve, update, delete specific RAK claims
    # Pay It Forward functionality
    path(
        "payitforward/<int:rak_id>/", PayItForwardView.as_view(), name="pay-it-forward"
    ),  # Create Pay It Forward RAK
    path(
        "payitforwards/",
        PayItForwardListCreateView.as_view(),
        name="payitforward-list-create",
    ),  # List and create PayItForward instances
    path(
        "payitforwards/<int:pk>/",
        PayItForwardDetailView.as_view(),
        name="payitforward-detail",
    ),  # Retrieve, update, delete a specific PayItForward instance
    # Collaboration functionality
    path(
        "rakposts/<int:rak_id>/enable_collaboration/",
        EnableCollaborationView.as_view(),
        name="enable-collaboration",
    ),  # Enable collaboration on RAK
    path(
        "rakposts/<int:rak_id>/join/", JoinRAKView.as_view(), name="join-rak"
    ),  # Join RAK as collaborator
    path(
        "rakposts/<int:pk>/", RandomActOfKindnessDetail.as_view(), name="rakpost-detail"
    ),
]
