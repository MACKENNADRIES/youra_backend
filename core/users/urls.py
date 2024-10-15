from django.urls import path
from .views import CustomUserList, CustomUserDetail

urlpatterns = [
    path('', CustomUserList.as_view(), name='user-list'),  # List and create users
    path('<int:pk>/', CustomUserDetail.as_view(), name='user-detail'),  # Detail view for specific users
]