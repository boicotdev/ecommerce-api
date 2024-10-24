from rest_framework.serializers import ModelSerializer
from .models import (
    Product,
    ProductCart,
    Order,
    OrderProduct,
    Category,
    Cart
)
from rest_framework import serializers

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source="category")

    def get_category(self, obj):
        return obj.category.name if obj.category else None

    category = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['name', 'price', 'sku', 'description', 'stock', 'category_id',
                  'recommended', 'best_seller', 'main_image', 'category']


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
        depth = 1


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
