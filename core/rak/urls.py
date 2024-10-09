from django.urls import path
from .views import RandomActOfKindnessList, RandomActOfKindnessDetail, RAKClaimList, ClaimActionList

urlpatterns = [
    path('rakposts/', RandomActOfKindnessList.as_view(), name='rakpost-list'),
    path('rakposts/<int:pk>/', RandomActOfKindnessDetail.as_view(), name='rakpost-detail'),
    path('claimedraks/', RAKClaimList.as_view(), name='rakclaim-list'),
    path('claimactions/', ClaimActionList.as_view(), name='claimaction-list'),
]
