from django.contrib import admin
from .models import (
    Product,
    ProductCart,
    OrderProduct,
    Order,
    Category,
    Cart,
    ProductReview
)

admin.site.register([Product, ProductCart, OrderProduct, Order, Category, Cart, ProductReview])
