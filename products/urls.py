from django.urls import path

from .views import (
    ProductCreateView,
    CategoryCreateView
)

urlpatterns = [
    path("products/categories/create/", CategoryCreateView.as_view()), #creata a new category
    path("products/create/", ProductCreateView.as_view()), #create a new product
]