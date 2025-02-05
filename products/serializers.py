from rest_framework.serializers import ModelSerializer
from .models import (
    Product,
    ProductCart,
    Order,
    OrderProduct,
    Category,
    Cart,
    ProductReview, Shipment, Payment, Coupon
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

class ProductReviewSerializer(ModelSerializer):
    class Meta:
        model = ProductReview
        fields ='__all__'

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

class ShipmentSerializer(ModelSerializer):
    class Meta:
        model = Shipment
        '''fields = [
            "customer_id",
            "order_id",
            "shipment_address",
            "shipment_city",
            "shipment_date_post_code",
        ]'''
        fields = '__all__'

    def validate_customer_id(self, value):
        if not value:
            raise serializers.ValidationError("El campo customer_id es obligatorio.")
        return value

    def validate_order_id(self, value):
        if Shipment.objects.filter(order_id=value).exists():
            raise serializers.ValidationError(
                "Ya existe un envío asociado a esta orden."
            )
        return value


class PaymentSerializer(ModelSerializer):
    """
    Serialize a `Payment` object and handle all logic to create a payment register
    ----
    """

    class Meta:
        model = Payment
        fields = '__all__'
        depth = 1

class CouponSerializer(ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
