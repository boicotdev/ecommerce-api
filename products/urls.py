from django.urls import path

from products.shipments.views import ShipmentCreateView, ShipmentListView, ShipmentUpdateView
from purchases.views import PurchaseCreateUpdateView, PurchaseDeleteView, PurchaseListView, PurchaseDetailView
from .payments.views import CreatePaymentPreference, MercadoPagoPaymentView, PaymentDetailsViewView, \
    PaymentCreateView, GenerateSalesReportView
from .views import (
    ProductCreateView,
    ProductListView,
    ProductDetailsView,
    ProductUpdateView,
    ProductRemoveView,
    CouponsCreateView,
    CouponUpdateView,
    CouponDeleteView,
    CouponsAdminRetrieveView,
    CouponCodeCheckView,
    UnitOfMeasureView,

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
    CartUserDelete, CartItemCreateView, CartExistView,
)

from products.orders.views import (
    OrderCreateView,
    OrderUserList,
    OrderUserRemove,
    OrderUserCancelView,
    OrdersDashboardView, OrderDashboardDetailsView, AdminOrderCreateView, OrderDashboardUpdateView
)

from products.product_order.views import (
    OrderProductCreateView,
)

from products.product_cart.views import (
    ProductCartCreateView, ProductCartUserList, ProductCartUserRemove, ProductCartHasChanged,
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
    path("carts/items/create/", CartItemCreateView.as_view()), #cart item create view
    path("carts/",  CartUserListView.as_view()), #list all carts of some user
    path("carts/delete/", CartUserDelete.as_view()), #remove a unique cart
    path("carts/check/", CartExistView.as_view()), #remove a unique cart

    #------------------------ orders endpoints --------------------------
    path("carts/orders/create/", OrderCreateView.as_view()), #create a new user order
    path("carts/orders/list/", OrderUserList.as_view()), #retrieve all orders of a user
    path("carts/orders/order/delete/", OrderUserRemove.as_view()), #delete an order
    path("orders/order/cancel/", OrderUserCancelView.as_view()), #cancel an order
    path("dashboard/orders/", OrdersDashboardView.as_view()), #retrieve all user orders
    path("dashboard/order/details/", OrderDashboardDetailsView.as_view()), #retrieve details of an order
    path("dashboard/order/create/", AdminOrderCreateView.as_view()),
    path("dashboard/order/update/", OrderDashboardUpdateView.as_view()),


    #------------------------- product-orders endpoints -------------------
    path("carts/orders/product-orders/create/", OrderProductCreateView.as_view()),

    #------------------------- product-cart endpoints --------------------
    path("carts/products/create/", ProductCartCreateView.as_view()), #add a new product to cart
    path("carts/products/list/", ProductCartUserList.as_view()), #retrieve all products per user into a cart
    path("carts/changes/check/", ProductCartHasChanged.as_view()), #retrieve all products per user into a cart
    path("carts/products/remove/", ProductCartUserRemove.as_view()), #remove a product from a given cart

    #-------------------------- Shipments endpoints --------------------
    path("orders/shipments/create/", ShipmentCreateView.as_view()), #create a new shipment
    path("orders/shipments/", ShipmentListView.as_view()), #retrieve all shipments
    path("orders/shipments/update/", ShipmentUpdateView.as_view()), #update a Shipment admin permissions are required

    #---------------------------- Coupons endpoints -----------------------
    path("coupons/", CouponsAdminRetrieveView.as_view()), #retrieve all coupons available on the shop
    path("coupons/validate/", CouponCodeCheckView.as_view()), #check if a coupon is valid
    path("coupons/create/", CouponsCreateView.as_view()), #create a new coupon
    path("coupons/update/", CouponUpdateView.as_view()), #update a single coupon
    path("coupons/delete/", CouponDeleteView.as_view()), #delete a single coupon

    #--------------------------------- Payments ---------------------------
    path("orders/carts/payments/", PaymentDetailsViewView.as_view()),
    path("payment/process/", PaymentCreateView.as_view()),
    path("payment/preferences/", CreatePaymentPreference.as_view()),
    path("process_payment/", MercadoPagoPaymentView.as_view()),
    path("sales-report/<str:order_id>/", GenerateSalesReportView.as_view(), name="sales-report"),


    #------------------------------------ Purchases -----------------------------
    path("purchases/", PurchaseCreateUpdateView.as_view()), # handle purchase creation
    path("purchases/delete/", PurchaseDeleteView.as_view()), # handle purchase deletion
    path("purchases/list/", PurchaseListView.as_view(), name="purchase-list"),  # Retrieve all purchases
    path("purchases/details/<str:id>/", PurchaseDetailView.as_view(), name="purchase-detail"),

    path("units-of-measure/", UnitOfMeasureView.as_view()), #Only GET Method to retrieve all measure units
    path("units-of-measure/create/", UnitOfMeasureView.as_view()), #Only POST Method
    path("units-of-measure/<int:unit_id>/", UnitOfMeasureView.as_view()), #GET PUT DELETE Methods
]
