import uuid
import random
import string
from abc import abstractmethod

from django.core.validators import RegexValidator
from django.db import models

def generate_unique_id(user_dni, purchase=False):
    """
    Genera un ID único con los siguientes formatos:
    - Orden: "ECCXX9YYYYYYYY" (XX = letras, 9 = número, YYYYYYYY = DNI)
    - Compra: "COMP-ECCXX9YY" (XX = letras, 9 = número, YY = últimos 2 dígitos del DNI)
    """

    while True:
        if purchase:
            # Prefijo para compras: COMP-ECCXX9YY (últimos 2 dígitos del DNI)
            prefix = f"{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}{random.randint(0, 9)}"
            unique_id = f"COMP-ECC{prefix}{str(user_dni)[-4:]}"  # Últimos 2 dígitos del DNI

            if not Purchase.objects.filter(id=unique_id).exists():
                return unique_id

        else:
            # Prefijo para órdenes: ECCXX9YYYYYYYY
            prefix = f"{random.choice(string.ascii_uppercase)}{random.choice(string.ascii_uppercase)}{random.randint(0, 9)}"
            unique_id = f"ECC{prefix}{user_dni}"

            if not Order.objects.filter(id=unique_id).exists():
                return unique_id


options = (
    ("CANASTILLA", "CANASTILLA"),
    ("MANOJO", "MANOJO"),
    ("BULTO", "BULTO"),
    ("CAJA", "CAJA"),
    ("ATADOS", "ATADOS"),
    ("DOCENA", "DOCENA"),
    ("BOLSAS", "BOLSAS"),
    ("GUACAL", "GUACAL"),
    ("BANDEJA", "BANDEJA"),
    ("ESTUCHE", "ESTUCHE"),
    ("PONY", "PONY"),
    ("KG", "KG"),
)

class Category(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=50)

    def __str__(self):
        return f"Category: {self.name}"


class UnitOfMeasure(models.Model):
    """
    Represent a measure unity, a product can be related to `UnitOfMeasure`
    Set all choices are required by your application.
    """
    unity = models.CharField(max_length=30, choices=options)
    weight = models.IntegerField()

    def __str__(self):
        return f"Unit Of Measure {self.unity} | ID {self.id} | Weight {self.weight} Lbs"

class Product(models.Model):
    sku = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=20)
    description = models.TextField(max_length=1024)
    price = models.FloatField()
    stock = models.IntegerField(default=1)
    measure_unity = models.ForeignKey(UnitOfMeasure, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="unity")
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    rank = models.IntegerField(default=0)
    recommended = models.BooleanField(default=False)
    best_seller = models.BooleanField(default=False)
    score = models.IntegerField(blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)
    has_discount = models.BooleanField(default=False, null=True, blank=True)
    purchase_price = models.FloatField(default=0, blank=True, null=True)
    discount_price = models.FloatField(default=0, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    # ------------------------ images --------------------
    main_image = models.ImageField(
        upload_to="products/", default="products/dummie_image.jpeg"
    )
    first_image = models.ImageField(
        upload_to="products/", default="products/dummie_image.jpeg"
    )
    second_image = models.ImageField(
        upload_to="products/", default="products/dummie_image.jpeg"
    )

    def __str__(self):
        return f"Product: {self.name} (SKU: {self.sku}, Stock: {self.stock} KG, Price: ${self.price})"


class Cart(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    creation_date = models.DateTimeField(verbose_name="Cart creation", auto_now=True)
    last_updated = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Cart: {self.name} (ID: {self.id}, User: {self.user.username})"


class ProductCart(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    measure_unity = models.ForeignKey(UnitOfMeasure, blank=True, null=True, on_delete=models.SET_NULL, verbose_name="unity")


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

    id = models.CharField(primary_key=True, max_length=20)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS, default="PENDING")


    def save(self, *args, **kwargs):
        if not self.id:  # Solo generar el ID si no existe
            user_dni = getattr(self.user, 'dni', "00000000")  # Obtener el DNI del usuario o usar por defecto
            self.id = generate_unique_id(user_dni)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Order {self.id} | {self.status} | {self.creation_date} | Last updated: {self.last_updated} | User: {self.user.username}"


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField()
    quantity = models.IntegerField()
    measure_unity = models.ForeignKey(UnitOfMeasure, blank=True, null=True, on_delete=models.SET_NULL,
                                      verbose_name="unity")

    def __str__(self):
        return f"OrderProduct: {self.product.name} (x{self.quantity}) in Order {self.order.pk}"


class ProductReview(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    review = models.TextField(max_length=525)
    rank = models.IntegerField(choices=[(n, str(n)) for n in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now_add=True, blank=True, null=True)


    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name} - {self.rank}★"


class Shipment(models.Model):
    @abstractmethod
    def set_tracking_number(self):
        return f'ECC-{str(uuid.uuid4())[:15].replace("-", "")}'

    id = models.CharField(max_length=100, default=set_tracking_number, primary_key=True)
    customer = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name="shipments")
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
        ("BANK_TRANSFER", "BANK_TRANSFER"),
        ("NEQUI", "NEQUI")
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
    last_updated = models.DateTimeField(auto_now_add=True, blank=True, null=True)

    def __str__(self):
        return f"Payment {self.id} | {self.payment_status} | ${self.payment_amount}"


class Coupon(models.Model):
    created_by = models.ForeignKey('users.User', null=True, blank=True, on_delete=models.CASCADE)
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


class Purchase(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    purchased_by = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, blank=True,
                                     related_name="user_admin")
    purchase_date = models.DateTimeField(auto_now_add=False, blank=True, null=True)
    last_updated = models.DateTimeField(auto_now=True)
    total_amount = models.FloatField(default=0)  # Total de compra
    global_sell_percentage = models.FloatField(default=10)  # Porcentaje de venta global
    estimated_profit = models.FloatField(default=0)  # Ganancia estimada

    def save(self, *args, **kwargs):
        if not self.id:
            admin_dni = getattr(self.purchased_by, 'dni', "00000000")
            self.id = generate_unique_id(admin_dni, purchase="True")
        super().save(*args, **kwargs)

    def update_totals(self):
        """Recalcula el total de la compra y la ganancia estimada."""
        total_cost = sum(item.subtotal() for item in self.purchase_items.all())
        self.total_amount = total_cost
        self.estimated_profit = sum(item.estimated_profit() for item in self.purchase_items.all())
        self.save()

    def __str__(self):
        return f"Purchase {self.id} | Total: ${self.total_amount} | Profit: ${self.estimated_profit}"



class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="purchase_items")
    product = models.ForeignKey(Product, blank=True, null=True, on_delete=models.SET_NULL)
    quantity = models.IntegerField()
    purchase_price = models.FloatField()  # Precio de compra unitario
    sell_percentage = models.FloatField(null=True, blank=True)
    unit_measure = models.ForeignKey(UnitOfMeasure, blank=True, null=True, on_delete=models.SET_NULL)

    def get_sell_percentage(self):
        """Obtiene el porcentaje de venta: usa el del item si está definido, de lo contrario usa el de Purchase."""
        return self.sell_percentage if self.sell_percentage is not None else self.purchase.global_sell_percentage

    def subtotal(self):
        """Calcula el costo total de compra de este producto."""
        return self.quantity * self.purchase_price

    def estimated_profit(self):
        """Calcula la ganancia estimada en base al porcentaje de venta y el peso de la unidad de medida."""
        sell_percentage = self.get_sell_percentage()
        profit_per_unit = self.purchase_price * (sell_percentage / 100)
        return self.quantity * profit_per_unit

    def sale_price_per_weight(self):
        """Calcula el precio de venta basado en el subtotal, el peso de la unidad de medida y la cantidad comprada."""
        if not self.unit_measure or self.unit_measure.weight == 0:
            return 0  # Evita división por cero o errores con None

        sell_percentage = self.get_sell_percentage()

        # Aplicar el porcentaje de venta al subtotal
        subtotal_with_margin = self.subtotal() + (self.subtotal() * (sell_percentage / 100))

        # Calcular precio de venta basado en el peso de la unidad de medida y cantidad comprada
        return subtotal_with_margin / (self.unit_measure.weight * self.quantity)

    def __str__(self):
        if self.product:
            return f"{self.quantity}x {self.product.name} @ ${self.purchase_price} (Sell %: {self.get_sell_percentage()}%)"
        return f"{self.quantity}x Desconocido @ ${self.purchase_price} (Sell %: {self.get_sell_percentage()}%)"


class MissingItems(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="missing_item")
    last_updated = models.DateTimeField(auto_now_add=True)
    stock = models.IntegerField(default=1)
    missing_quantity = models.IntegerField(default=0)
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="pending_order")

    def __str__(self):
        return f"Item {self.product.sku} | Order {self.order.id} | Missing {self.missing_quantity}"