from django.urls import path

from .views import (
    ProductCreateView, 
    ProductListView,
    ProductDetailsView,
    ProductUpdateView,
    ProductRemoveView

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
    CartUserDelete,
)

from products.orders.views import (
    OrderCreateView,
    OrderUserList,
    OrderUserRemove
)

from products.product_order.views import (
    OrderProductCreateView,
)

from products.product_cart.views import (
    ProductCartCreateView, ProductCartUserList, ProductCartUserRemove,
)
urlpatterns = [

    path("products/categories/create/", CategoryCreateView.as_view()), #create a new category
    path("products/create/", ProductCreateView.as_view()), #create a new product
    path("products/categories/", CategoryListView.as_view()), #list all categories
    path("products/categories/update/", CategoryUpdateView.as_view()), #update a category
    path("products/categories/remove/", CategoryRemoveView.as_view()), #remove a category
    path("products/list/", ProductListView.as_view()), #retrieve all products
    path("products/product/details/", ProductDetailsView.as_view()), #retrieve a single products
    path("products/product/update/", ProductUpdateView.as_view()),
    path("products/product/remove/", ProductRemoveView.as_view()), # remove a single product

    #------------------------ carts endpoints -----------------------------
    path("carts/create/", CartCreateView.as_view()), #create carts
    path("orders/carts/",  CartUserListView.as_view()), #list all carts of some user
    path("orders/carts/delete/", CartUserDelete.as_view()), #remove a unique cart

    #------------------------ orders endpoints --------------------------
    path("carts/orders/create/", OrderCreateView.as_view()),
    path("carts/orders/list/", OrderUserList.as_view()),
    path("carts/orders/order/delete/", OrderUserRemove.as_view()),

    #------------------------- product-orders endpoints -------------------
    path("carts/orders/product-orders/create/", OrderProductCreateView.as_view()),

    #------------------------- product-cart endpoints --------------------
    path("carts/products/create/", ProductCartCreateView.as_view()), #add a new product to cart
    path("carts/products/list/", ProductCartUserList.as_view()), #retrieve all products per user into a cart
    path("carts/products/remove/", ProductCartUserRemove.as_view()), #remove a product from a given cart
    
]
