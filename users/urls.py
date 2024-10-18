from django.urls import path

from .views import (
    UserCreateView, 
    UserListView, 
    UserUpdateView, 
    UserDeleteView, 
    CustomTokenObtainPairView
)


urlpatterns = [
    path("users/create/", UserCreateView.as_view()), #create a new user
    path("users/", UserListView.as_view()), #list all users into the database
    path("users/edit/", UserUpdateView.as_view()), #edit a single user
    path("users/delete/", UserDeleteView.as_view()), #delete a single user
    path("users/token/obtain/", CustomTokenObtainPairView.as_view()), #token obtain
]
