from django.urls import path, include
from .views import LoginView, RegisterView, UserInfoView, LogoutView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('register/', RegisterView.as_view(), name='register'),
    path('user-info/', UserInfoView.as_view(), name='user-info'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
