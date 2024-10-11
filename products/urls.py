from django.urls import path

from .views import (
    ProductCreateView,
)
from products.categories.views import (
    CategoryCreateView,
    CategoryListView,
    CategoryUpdateView,
    CategoryRemoveView
)
from products.carts.views import (
    CartCreateView,
    CartUserListView,
    CartUserDelete
)

urlpatterns = [

    path("products/categories/create/", CategoryCreateView.as_view()), #create a new category
    path("products/create/", ProductCreateView.as_view()), #create a new product
    path("products/categories/", CategoryListView.as_view()), #list all categories
    path("products/categories/update/", CategoryUpdateView.as_view()), #update a category
    path("products/categories/remove/", CategoryRemoveView.as_view()), #remove a category

    #------------------------ carts endpoints -----------------------------
    path("carts/create/", CartCreateView.as_view()), #create carts
    path("orders/carts/",  CartUserListView.as_view()), #list all carts of some user
    path("orders/carts/delete/", CartUserDelete.as_view()), #remove a unique cart
]