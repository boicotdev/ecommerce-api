from rest_framework.serializers import ModelSerializer

from users.models import User
from .models import (
    Product,
    ProductCart,
    Order,
    OrderProduct,
    Category,
    Cart,
    ProductReview, Shipment, Payment, Coupon, UnitOfMeasure, PurchaseItem, Purchase, MissingItems
)
from rest_framework import serializers

class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    def get_category(self, obj):
        return obj.category.name if obj.category else None

    def get_unity(self, obj):
        return obj.measure_unity.unity if obj.measure_unity else None

    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source="category")
    measure_unity = serializers.PrimaryKeyRelatedField(queryset=UnitOfMeasure.objects.all())
    category = serializers.SerializerMethodField()
    unity = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['name', 'price', 'sku', 'description', 'stock', 'category_id',
                  'recommended', 'best_seller', 'has_discount', 'discount_price', 'main_image', 'first_image', 'second_image', 'category', 'rank', 'measure_unity', 'unity']

        def create(self, **validated_data):
            print('validated data',validated_data)
            sku = validated_data.pop("sku", None)
            instance = self.Meta.model(**validated_data)
            if not sku:
                raise serializers.ValidationError({'sku': 'This field is required'})

            instance.sku = sku
            instance.save()
            return instance


class ProductReviewSerializer(ModelSerializer):
    class Meta:
        model = ProductReview
        fields ='__all__'


class UserDetailsSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['dni', 'email', 'username', 'first_name', 'last_name', 'address', 'phone', 'avatar']


class ProductCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCart
        fields = ['id', 'cart', 'product', 'quantity']
        depth = 1

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


class OrderProductSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)  # Serializa el producto relacionado

    class Meta:
        model = OrderProduct
        fields = ['id', 'product', 'price', 'quantity']  # No hay un campo 'products' en OrderProduct


class OrderSerializer(serializers.ModelSerializer):
    total = serializers.SerializerMethodField()
    products = OrderProductSerializer(source='orderproduct_set', many=True, read_only=True)

    @staticmethod
    def get_total(order):
        try:
            payment = Payment.objects.filter(order=order).first()
            return payment.payment_amount if payment else 0
        except Exception as e:
            print(f"Error en get_total: {e}")
            return 0

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), required=True)
    user_details = UserDetailsSerializer(source='user', read_only=True)
    payment = PaymentSerializer()

    class Meta:
        model = Order
        fields = ['id', 'user', 'user_details', 'payment', 'creation_date', 'last_updated', 'status', 'total', 'products']


class CartSerializer(ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'


class ShipmentSerializer(ModelSerializer):
    customer = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), write_only=True)
    customer_details = UserDetailsSerializer(source='customer', read_only=True)
    amount = serializers.SerializerMethodField()

    @staticmethod
    def get_amount(shipment):
        try:
            order = shipment.order  # Acceder directamente a la orden
            payment = Payment.objects.filter(order=order).first()  # Buscar el pago asociado

            if payment:
                return payment.payment_amount  # Devolver el monto pagado

            return 0  # Si no hay pago, devolver 0
        except Exception as e:
            print(f"Error en get_amount: {e}")  # Log del error
            return 0

    class Meta:
        model = Shipment
        fields = [
            'id', 'order', 'shipment_address', 'shipment_date',
            'shipment_city', 'shipment_date_post_code', 'status',
            'customer', 'customer_details', 'amount'
        ]

    def validate_customer(self, value):
        """Validar que el campo 'customer' sea obligatorio"""
        if not value:
            raise serializers.ValidationError("El campo customer es obligatorio.")
        return value

    def validate_order(self, value):
        """Evitar que una orden tenga más de un envío"""
        if Shipment.objects.filter(order=value).exists():
            raise serializers.ValidationError("Ya existe un envío asociado a esta orden.")
        return value


class CouponSerializer(ModelSerializer):
    class Meta:
        model = Coupon
        fields = '__all__'

class UnitOfMeasureSerializer(serializers.ModelSerializer):
    class Meta:
        model = UnitOfMeasure
        fields = '__all__'


class PurchaseItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.ReadOnlyField()
    estimated_profit = serializers.ReadOnlyField()
    sale_price_per_weight = serializers.ReadOnlyField()
    product = ProductSerializer()

    class Meta:
        model = PurchaseItem
        fields = ["id", "product", "quantity", "purchase_price", "sell_percentage", "unit_measure", "subtotal", "estimated_profit", "sale_price_per_weight"]

class PurchaseSerializer(serializers.ModelSerializer):
    purchase_items = PurchaseItemSerializer(many=True, read_only=True)
    estimated_profit = serializers.ReadOnlyField()


    class Meta:
        model = Purchase
        fields = ["id", "purchased_by", "purchase_date", "last_updated", "total_amount", "global_sell_percentage", "estimated_profit", "purchase_items"]
    def validate_global_sell_percentage(self, value):
        """Valida que el porcentaje de venta global sea al menos 10%"""
        if value is None or value < 10:
            raise serializers.ValidationError("El porcentaje de venta debe ser al menos 10%")
        return value


class MissingItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    order = OrderSerializer()
    class Meta:
        model = MissingItems
        fields = ['id', 'product', 'last_updated', 'stock', 'missing_quantity', 'order']