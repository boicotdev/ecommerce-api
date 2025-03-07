from django.core.validators import RegexValidator
from django.db import models
from users.models import User

class Category(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=50)

    def __str__(self):
        return f"Category: {self.name}"


class Product(models.Model):
    sku = models.CharField(max_length=30)
    name = models.CharField(max_length=20)
    description = models.TextField(max_length=1024)
    price = models.FloatField()
    stock = models.IntegerField(default=1)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    rank = models.IntegerField(default=0)
    recommended = models.BooleanField(default=False)
    best_seller = models.BooleanField(default=False)
    score = models.IntegerField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    main_image = models.ImageField(
        upload_to="static/images/products", default="static/images/products/dummie_image.jpeg"
    )
    first_image = models.ImageField(
        upload_to="static/images/products/", default="static/images/products/dummie_image.jpeg"
    )
    second_image = models.ImageField(
        upload_to="static/images/products/", default="static/images/products/dummie_image.jpeg"
    )

    def __str__(self):
        return f"Product: {self.name} (SKU: {self.sku}, Stock: {self.stock} KG, Price: ${self.price})"


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    creation_date = models.DateTimeField(verbose_name="Cart creation", auto_now=True)

    def __str__(self):
        return f"Cart: {self.name} (ID: {self.id}, User: {self.user.username})"


class ProductCart(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"ProductCart: {self.product.name} x{self.quantity} in {self.cart.name}"


class Order(models.Model):
    STATUS = (
        ("PENDING", "PENDING"),
        ("PROCESSING", "PROCESSING"),
        ("SHIPPED", "SHIPPED"),
        ("OUT_FOR_DELIVERY", "OUT_FOR_DELIVERY"),
        ("DELIVERED", "DELIVERED"),
        ("CANCELLED", "CANCELLED"),
        ("RETURNED", "RETURNED"),
        ("FAILED", "FAILED"),
        ("ON_HOLD", "ON_HOLD"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS, default=STATUS[0])

    def __str__(self):
        return f"Order {self.pk} | {self.status} | {self.creation_date} | User: {self.user.username}"


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField()
    quantity = models.IntegerField()

    def __str__(self):
        return f"OrderProduct: {self.product.name} (x{self.quantity}) in Order {self.order.pk}"


class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    review = models.TextField(max_length=525)
    rank = models.IntegerField(choices=[(n, str(n)) for n in range(1, 6)])

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name} - {self.rank}★"


class Shipment(models.Model):
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="shipments")
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="shipment")
    shipment_date = models.DateTimeField(auto_now_add=True)
    shipment_address = models.CharField(max_length=255)
    shipment_city = models.CharField(max_length=50)
    postal_code_validator = RegexValidator(regex=r"^\d{4,10}$", message="El código postal debe contener entre 4 y 10 dígitos.")
    shipment_date_post_code = models.CharField(max_length=10, validators=[postal_code_validator])

    PENDING = "PENDING"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"

    SHIPMENT_STATUS_CHOICES = [
        (PENDING, PENDING),
        (SHIPPED, SHIPPED),
        (DELIVERED, DELIVERED),
        (CANCELLED, CANCELLED),
    ]

    status = models.CharField(max_length=10, choices=SHIPMENT_STATUS_CHOICES, default=PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shipment {self.id} | {self.get_status_display()} | {self.shipment_address}, {self.shipment_city}"


class Payment(models.Model):
    PAYMENT_METHODS = (
        ("CASH", "CASH"),
        ("DEBIT_CARD", "DEBIT_CARD"),
        ("CREDIT_CARD", "CREDIT_CARD"),
    )

    PAYMENT_STATUS = (
        ("APPROVED", "APPROVED"),
        ("PENDING", "PENDING"),
        ("IN_PROCESS", "IN_PROCESS"),
        ("REJECTED", "REJECTED"),
        ("CANCELED", "CANCELED"),
        ("REFUNDED", "REFUNDED"),
        ("CHARGED_BACK", "CHARGED_BACK"),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_amount = models.FloatField(verbose_name="payment_amount")
    payment_date = models.DateTimeField(auto_created=True)
    payment_method = models.CharField(max_length=15, choices=PAYMENT_METHODS)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS)

    def __str__(self):
        return f"Payment {self.id} | {self.payment_status} | ${self.payment_amount}"


class Coupon(models.Model):
    coupon_code = models.CharField(max_length=15)
    discount = models.IntegerField()
    creation_date = models.DateTimeField(auto_now=True)
    expiration_date = models.DateField()
    is_active = models.BooleanField(default=True)
    discount_type = models.CharField(choices=(("PERCENTAGE", "PERCENTAGE"), ("FIXED", "FIXED")), max_length=12)

    def is_valid(self):
        from django.utils.timezone import now

        current_date = now().date()
        return self.is_active and self.expiration_date > current_date

    def __str__(self):
        if self.discount_type == "FIXED":
            return f"Coupon {self.coupon_code} | {self.discount_type} | ${self.discount} | Expires: {self.expiration_date}"
        else:
            return f"Coupon {self.coupon_code} | {self.discount_type} | {self.discount}% | Expires: {self.expiration_date}"
