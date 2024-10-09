"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from users.views import CustomAuthToken
from rak.views import UpdateRAKStatusView

urlpatterns = [
    # Admin URL
    path('admin/', admin.site.urls),

    # Include URLs from the 'rak' app
    path('rak/', include('rak.urls')),

    # Include URLs from the 'users' app
    path('users/', include('users.urls')),

    # Django REST Framework login and logout views for the browsable API
    path('api-auth/', include('rest_framework.urls')),

    # Token-based authentication for API access
    path('api-token-auth/', CustomAuthToken.as_view(), name='api_token_auth'),

    path('rakposts/<int:pk>/status/', UpdateRAKStatusView.as_view(), name='update-rak-status'),
]
