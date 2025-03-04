from django.urls import path
from .views import RegisterView, LoginView, UserListView, UserDeleteView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('users/', UserListView.as_view(), name='user-list'),  
    path('users/<int:pk>/', UserDeleteView.as_view(), name='user-delete'),  
]
