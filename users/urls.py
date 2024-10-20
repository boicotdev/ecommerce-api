from django.urls import path

from .views import (
    UserCreateView, 
    UserListView, 
    UserUpdateView, 
    UserDeleteView,
    UserDetailsView,
    CustomTokenObtainPairView,
    CommentView,
)


urlpatterns = [
    path("users/create/", UserCreateView.as_view()), #create a new user
    path("users/", UserListView.as_view()), #list all users into the database
    path("users/user/", UserDetailsView.as_view()), #retrieve all info of a single user
    path("users/user/update/", UserUpdateView.as_view()), #edit a single user
    path("users/delete/", UserDeleteView.as_view()), #delete a single user
    path("users/token/obtain/", CustomTokenObtainPairView.as_view()), #token obtain
    path("users/comments/comment/", CommentView.as_view()), #create a new comment
]
