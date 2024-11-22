from django.db import models
from users.models import User

class Category(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Product(models.Model):
    # TODO add sku property as PK, add image field
    sku = models.CharField(max_length=30)
    name = models.CharField(max_length=20)
    description = models.TextField(max_length=1024)
    price = models.FloatField()
    stock = models.IntegerField(default=1)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    rank = models.IntegerField(default=0)
    recommended = models.BooleanField(default=False)
    best_seller = models.BooleanField(default=False)
    score = models.IntegerField(blank=True, null= True)
    slug = models.SlugField(blank=True, null= True)
    main_image = models.ImageField(upload_to="static/images/products", default="static/images/products/dummie_image.jpeg")
    first_image = models.ImageField(upload_to="static/images/products/", default="static/images/products/dummie_image.jpeg")
    second_image = models.ImageField(upload_to="static/images/products/", default="static/images/products/dummie_image.jpeg")

    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=100)
    creation_date = models.DateTimeField(verbose_name="Cart creation", auto_now= True)

    def __str__(self):
        return self.name

class ProductCart(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"( Product - {self.product} | Cart - {self.cart.name} )"

class Order(models.Model):
    #FIXME change status tuple
    STATUS = (
        ("DELIVERED", "DELIVERED"),
        ("CANCELLED", "CANCELLED"),
        ("PENDING", "PENDING"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now=True)
    status = models.CharField(max_length=12, choices=STATUS)

    def __str__(self):
        return f"(Order: {self.pk} | Status - {self.status} | Created - {self.creation_date} | User - {self.user})"

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField()
    quantity = models.IntegerField()

    def __str__(self):
        return f"{self.product.name} - {self.order}"


class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    review = models.TextField(max_length=525)
    rank = models.IntegerField(choices=[(n, str(n)) for n in range(1, 6)])

    def __str__(self):
        return f"El usuario {self.user.username} calificó el producto {self.product.name} con una calificación de {self.rank} puntos"

class Shipment(models.Model):
    """
    Create a new shipment object in the shop
    """
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    shipment_date = models.DateTimeField(auto_now=True)
    shipment_address = models.CharField(max_length=50)
    shipment_city = models.CharField(max_length=30)
    shipment_date_post_code = models.CharField(max_length=10)

    def __str__(self):
        return f"Shipment to ({self.shipment_address} - {self.shipment_city})"

class Payment(models.Model):
    PAYMENT_METHODS = (
        ("CASH", "CASH"),
        ("DEBIT_CARD", "DEBIT_CARD"),
        ("CREDIT_CARD", "CREDIT_CARD")
    )

    PAYMENT_STATUS = (
        ("APPROVED", "APPROVED"),
        ("DECLINED", "DECLINED"),
        ("WAITING", "WAITING")
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    payment_amount = models.FloatField(2)
    payment_date = models.DateTimeField(auto_created=True)
    payment_method = models.CharField(max_length=15, choices= PAYMENT_METHODS)
    payment_status = models.CharField(max_length=15, choices= PAYMENT_STATUS)

    def __str__(self):
        return f"{self.order} - {self.payment_status}"








