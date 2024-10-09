from django.urls import path
from .views import RandomActOfKindnessList, RandomActOfKindnessDetail, RAKClaimList, RAKClaimDetail, ClaimActionList, PayItForwardView, ClaimRAKView, CompleteRAKView

urlpatterns = [
    path('rakposts/', RandomActOfKindnessList.as_view(), name='rakpost-list'),
    path('rakposts/<int:pk>/', RandomActOfKindnessDetail.as_view(), name='rakpost-detail'),
    path('claimedraks/', RAKClaimList.as_view(), name='rakclaim-list'),
    path('rakclaims/<int:pk>/', RAKClaimDetail.as_view(), name='rakclaim-detail'),
    path('claimactions/', ClaimActionList.as_view(), name='claimaction-list'),
    path('payitforward/<int:pk>/', PayItForwardView.as_view(), name='payitforward'),  # Add this line
    # URL for claiming a Random Act of Kindness
    path('rakposts/<int:rak_id>/claim/', ClaimRAKView.as_view(), name='claim-rak'),
    # URL for completing a Random Act of Kindness
    path('rakposts/<int:rak_id>/complete/', CompleteRAKView.as_view(), name='complete-rak'),
]
