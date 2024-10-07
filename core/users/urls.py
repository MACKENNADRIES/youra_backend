from django.urls import path
from .views import CustomUserList, CustomUserDetail

urlpatterns = [
    path('users/', CustomUserList.as_view(), name='user-list'),
    path('users/<int:pk>/', CustomUserDetail.as_view(), name='user-detail'),
]
