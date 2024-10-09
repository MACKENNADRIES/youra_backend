from django.urls import path
from .views import CustomUserList, CustomUserDetail

urlpatterns = [
    path('', CustomUserList.as_view(), name='user-list'),  
    path('<int:pk>/', CustomUserDetail.as_view(), name='user-detail'),
]
