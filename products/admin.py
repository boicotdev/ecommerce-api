from django.contrib import admin
from .models import (
    Product,
    ProductCart,
    OrderProduct,
    Order,
    Category,
    Cart,
    ProductReview,
    Shipment,
    Payment, Coupon, UnitOfMeasure, Purchase, PurchaseItem, MissingItems
)

admin.site.register([Product, ProductCart, OrderProduct, Order, Category, Cart,
                     ProductReview, Shipment, Payment, Coupon, UnitOfMeasure,
                     Purchase, PurchaseItem, MissingItems
                     ])