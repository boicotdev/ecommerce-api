from django.db import models
from users.models import User

class Category(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Product(models.Model):
    # Todo : add sku property as PK, add image field
    sku = models.CharField(max_length=30)
    name = models.CharField(max_length=20)
    description = models.TextField(max_length=1024)
    price = models.FloatField()
    stock = models.IntegerField(default=1)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

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
        return f"{self.product} - {self.cart.name}"

class Order(models.Model):
    STATUS = (
        ("DELIVERED", "DELIVERED"),
        ("CANCELLED", "CANCELLED"),
        ("PENDING", "PENDING"),
        ("PAY", "PAY")
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateField(auto_now=True)
    status = models.CharField(max_length=12, choices=STATUS)

    def __str__(self):
        return f"(Order: {self.id} | Created - {self.creation_date} | User - {self.user})"

class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.FloatField()
    quantity = models.IntegerField()

    def __str__(self):
        return f"Producto {self.product.name} - {self.order}"

