from django.urls import path
from .views import (
    RandomActOfKindnessList, RandomActOfKindnessDetail, RAKClaimList, RAKClaimDetail,
    PayItForwardView, UserProfileView, UserProfileListView, LeaderboardView,
    EnableCollaborationView, JoinRAKView, CustomAuthToken
)

urlpatterns = [
    path('rakposts/', RandomActOfKindnessList.as_view(), name='rakpost-list'),
    path('rakposts/<int:pk>/', RandomActOfKindnessDetail.as_view(), name='rakpost-detail'),
    path('claimedraks/', RAKClaimList.as_view(), name='rakclaim-list'),
    path('rakclaims/<int:pk>/', RAKClaimDetail.as_view(), name='rakclaim-detail'),
    path('payitforward/<int:rak_id>/', PayItForwardView.as_view(), name='pay_it_forward'),
    path('userprofile/', UserProfileView.as_view(), name='user-profile'),
    path('userprofiles/', UserProfileListView.as_view(), name='user-profiles'),
    path('rakposts/<int:rak_id>/enable_collaboration/', EnableCollaborationView.as_view(), name='enable-collaboration'),
    path('rakposts/<int:rak_id>/join/', JoinRAKView.as_view(), name='join-rak'),
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('token/', CustomAuthToken.as_view(), name='custom-token-auth'),  # Token login without 'api'
]
