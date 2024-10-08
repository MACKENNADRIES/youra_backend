from django.urls import path
from .views import RAKPostList, RAKPostDetail, ClaimedRAKList, ClaimActionList

urlpatterns = [
    path('rakposts/', RAKPostList.as_view(), name='rakpost-list'),
    path('rakposts/<int:pk>/', RAKPostDetail.as_view(), name='rakpost-detail'),
    path('claimedraks/', ClaimedRAKList.as_view(), name='claimedrak-list'),
    path('claimactions/', ClaimActionList.as_view(), name='claimaction-list'),
    
]
