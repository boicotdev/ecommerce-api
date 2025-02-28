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
                  'recommended', 'best_seller', 'main_image', 'category', 'rank', 'score']


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
        fields = ['id', 'cart', 'product', 'quantity']

    def create(self, validated_data):
        """
        Si el producto ya está en el carrito, actualiza la cantidad en lugar de crear un nuevo objeto.
        """
        product = validated_data.get('product')
        quantity = validated_data.get('quantity', 0)

        # Buscar si el producto ya está en el carrito
        existing_item = ProductCart.objects.filter(product=product).first()

        if existing_item:
            existing_item.quantity += quantity  # Sumar la nueva cantidad
            existing_item.save()
            return existing_item  # Retornar el objeto actualizado
        else:
            return super().create(validated_data)  # Crear un nuevo registro si no existe


class PaymentSerializer(ModelSerializer):
    """
    Serialize a `Payment` object and handle all logic to create a payment register
    ----
    """

    class Meta:
        model = Payment
        fields = '__all__'
        depth = 1


class OrderSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()

    @staticmethod
    def get_total(order):
        try:
            order_products = OrderProduct.objects.filter(order=order)
            total = sum(p.price * p.quantity for p in order_products)
            return total + 5000
        except Exception as e:
            return 0  # Devuelve 0 en caso de error para evitar que falle la serialización

    user = UserDetailsSerializer()
    payment = PaymentSerializer()
    class Meta:
        model = Order
        fields = ['id', 'user', 'payment', 'creation_date', 'status', 'total']


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



class CouponSerializer(ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'
