from logging import exception

from rest_framework.serializers import ModelSerializer

from users.models import User
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
        fields = ['id', 'name', 'price', 'sku', 'description', 'stock', 'category_id',
                  'recommended', 'best_seller', 'main_image', 'category']

class ProductReviewSerializer(ModelSerializer):
    class Meta:
        model = ProductReview
        fields ='__all__'



class UserDetailsSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'address']


class ProductCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCart
        fields = ['cart', 'product', 'quantity']
        extra_kwargs = {'cart': {'read_only': True}}  # Si no quieres que venga en la petición

    def create(self, validated_data):
        # Supongamos que asignas el cart desde el contexto
        cart = self.context.get('cart')
        if not cart:
            raise serializers.ValidationError("No se pudo obtener el carrito.")
        validated_data['cart'] = cart
        return super().create(validated_data)



class OrderSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()

    def get_total(self, order):
        try:
            order_products = OrderProduct.objects.filter(order=order)
            total = sum(p.price * p.quantity for p in order_products)
            return total
        except Exception as e:
            return 0  # Devuelve 0 en caso de error para evitar que falle la serialización

    user = UserDetailsSerializer()
    class Meta:
        model = Order
        fields = ['id', 'user', 'creation_date', 'status', 'total']




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
