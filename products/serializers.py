from rest_framework.serializers import ModelSerializer
from .models import (
    Product,
    ProductCart,
    Order,
    OrderProduct,
    Category,
    Cart
)

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(ModelSerializer):
    """
    Represents a `Product` on ecommerce
    """
    class Meta:
        model = Product
        fields = '__all__'

class ProductCartSerializer(ModelSerializer):
    """
    Represents a `ProductCart` item
    """

    class Meta:
        model = ProductCart
        fields = '__all__'
        depth = 2

class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OrderProductSerializer(ModelSerializer):
    """
    A product at a `Order`
    """

    class Meta:
        model = OrderProduct
        fields = '__all__'


class CartSerializer(ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'