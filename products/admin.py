from django.contrib import admin
from .models import (
    Product,
    ProductCart,
    OrderProduct,
    Order,
    Category,
    Cart,
)

admin.site.register([Product, ProductCart, OrderProduct, Order, Category, Cart])