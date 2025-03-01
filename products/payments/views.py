from datetime import datetime

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response
from rest_framework import status
import uuid

import mercadopago
from decouple import config
from users.models import User
from products.models import (
    Shipment,
    Payment, Order, OrderProduct, Product, ProductCart, Cart
)
from products.serializers import (
    ShipmentSerializer,
    PaymentSerializer
)

MP_ACCESS_TOKEN = config("MERCADO_PAGO_ACCESS_TOKEN")


class CreateShipmentView(APIView):
    """
    Handle all operations related to create a shipment order
    """

    def post(self, request):
        customer_id = request.data.get("customer", None)
        order_id = request.data.get("order", None)

        if not customer_id or not order_id:
            return Response({"message": "Customer ID and Order ID are required!"}, status = status.HTTP_400_BAD_REQUEST)

        if Shipment.objects.filter(order_id=request.data.get("order")).exists():
            return Response(
                {"error": "Ya existe un envío asociado a esta orden."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            serializer = ShipmentSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status = status.HTTP_201_CREATED)

            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class CreatePaymentPreference(APIView):
    def post(self, request):
        mercado_pago = mercadopago.SDK(MP_ACCESS_TOKEN)
        items = request.data.get("items", [])

        preference_data = {
            "items": items,
            "back_urls": {
                "success": "http://localhost:5173/payments/success/",
                "failure": "http://localhost:5173/payments/failure/",
                "pending": "http://localhost:5173/payments/pending/",
            },
            "auto_return": "approved",
        }

        # Crear la preferencia de pago en MercadoPago
        preference_response = mercado_pago.preference().create(preference_data)

        if preference_response["status"] == 201:
            user = request.user
            cart = Cart.objects.filter(user=user).first()  # Obtener el carrito del usuario
            pending_order = Order.objects.filter(user=user, status="PENDING").first()

            if not pending_order:
                # Crear una nueva orden si no hay una pendiente
                order = Order.objects.create(user=user, status="PENDING")

                # Crear lista de objetos para insertar en la BD en una sola operación
                order_products = []
                cart_products = []

                for item in items:
                    product = Product.objects.get(sku=item["sku"])
                    order_products.append(
                        OrderProduct(
                            order=order,
                            product=product,
                            price=item["unit_price"],
                            quantity=item["quantity"],
                        )
                    )
                    cart_products.append(
                        ProductCart(
                            cart=cart,
                            product=product,
                            quantity=item["quantity"],
                        )
                    )

                # Guardar los productos en una sola operación
                OrderProduct.objects.bulk_create(order_products)
                ProductCart.objects.bulk_create(cart_products)

                return Response(
                    {"order": order.pk, "preference_data": preference_response["response"]},
                    status=status.HTTP_201_CREATED,
                )

            # Obtener productos actuales de la orden y el carrito
            existing_order_products = {op.product.sku: op for op in pending_order.orderproduct_set.all()}
            existing_cart_products = {cp.product.sku: cp for cp in cart.productcart_set.all()}
            new_product_skus = {item["sku"] for item in items}

            # Listas para `bulk_update()`
            order_updates = []
            cart_updates = []

            for item in items:
                product = Product.objects.get(sku=item["sku"])

                # Actualizar cantidades en la orden
                if product.sku in existing_order_products:
                    existing_order_product = existing_order_products[product.sku]
                    existing_order_product.quantity = item["quantity"]
                    order_updates.append(existing_order_product)
                else:
                    OrderProduct.objects.create(
                        order=pending_order,
                        product=product,
                        price=item["unit_price"],
                        quantity=item["quantity"],
                    )

                # Actualizar cantidades en el carrito
                if product.sku in existing_cart_products:
                    existing_cart_product = existing_cart_products[product.sku]
                    existing_cart_product.quantity = item["quantity"]
                    cart_updates.append(existing_cart_product)
                else:
                    ProductCart.objects.create(
                        cart=cart,
                        product=product,
                        quantity=item["quantity"],
                    )

            # Guardar actualizaciones en una sola operación
            if order_updates:
                OrderProduct.objects.bulk_update(order_updates, ["quantity"])
            if cart_updates:
                ProductCart.objects.bulk_update(cart_updates, ["quantity"])

            # Eliminar productos que ya no están en la lista enviada
            order_products_to_remove = [
                op for sku, op in existing_order_products.items() if sku not in new_product_skus
            ]
            cart_products_to_remove = [
                cp for sku, cp in existing_cart_products.items() if sku not in new_product_skus
            ]

            if order_products_to_remove:
                OrderProduct.objects.filter(id__in=[op.id for op in order_products_to_remove]).delete()
            if cart_products_to_remove:
                ProductCart.objects.filter(id__in=[cp.id for cp in cart_products_to_remove]).delete()

            return Response(
                {"order": pending_order.pk, "preference_data": preference_response["response"]},
                status=status.HTTP_200_OK,
            )

        return Response({"detail": "Error creating preference!"}, status=status.HTTP_400_BAD_REQUEST)


class MercadoPagoPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        sdk = mercadopago.SDK(MP_ACCESS_TOKEN)
        request_options = mercadopago.config.RequestOptions()
        request_options.custom_headers = {
            'x-idempotency-key': request.data.get('idempotency_key', str(uuid.uuid4()))
        }

        try:
            user = request.user #authenticated user

            email = request.data["payer"]["email"]
            dni_type = request.data["payer"]["identification"]["type"]
            dni_number = request.data["payer"]["identification"]["number"]

            payment_data = {
                "transaction_amount": float(request.data.get("transaction_amount")),
                "token": request.data.get("token"),
                "description": "Compra de productos",
                "installments": int(request.data.get("installments")),
                "payment_method_id": request.data.get("payment_method_id"),
                "issuer_id": request.data.get("issuer_id"),
                "payer": {
                    "email": email,
                    "identification": {
                        "type": dni_type,
                        "number": dni_number
                    }
                }
            }

        except (TypeError, ValueError) as e:
            return Response(
                {"error": "Invalid payment data", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment_response = sdk.payment().create(request.data, request_options)
            payment = payment_response.get("response", {})

            # Obtener la orden del usuario autenticado
            order = Order.objects.filter(user=user, status="PENDING").first()
            if not order:
                return Response({"error": "No se encontró una orden asociada al usuario"}, status=status.HTTP_404_NOT_FOUND)

            return Response(payment, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(e)
            return Response(
                {"error": "Payment creation failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#cart details
class PaymentDetailsViewView(APIView):
    def get(self, request):
        order_id = request.query_params.get("order", None)
        if not  order_id:
            return Response({'message': 'Payment ID is required'}, status = status.HTTP_400_BAD_REQUEST)
        try:
            payment = Payment.objects.get(order = order_id)
            serializer = PaymentSerializer(payment, many=False)
            #if serializer.is_valid():
            return Response(data=serializer.data, status = status.HTTP_200_OK)
          #  return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        except Payment.DoesNotExist:
            return Response({'message': 'Payment not found'}, status = status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentCreateView(APIView):
    def post(self, request):
        print(request.data)
        order_id = request.data.get('order_id', None)
        payment_amount = request.data.get('payment_amount', None)
        payment_date = request.data.get('payment_date', None)
        payment_method = request.data.get('payment_method', None)
        payment_status = request.data.get('payment_status', None)

        if not all([order_id, payment_date, payment_amount, payment_method, payment_status]):
            return Response({'message': 'All fields are required'}, status = status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(pk=order_id)
            #check if exist a payment related to order_id
            if Payment.objects.filter(order=order_id).exists():
                return Response({'message': 'Order was payed successfully'}, status = status.HTTP_400_BAD_REQUEST)
            order.status = "PENDING" #change the order status to pend delivery
            order.save()
            payment = Payment.objects.create(
                order=order,
                payment_date=payment_date,
                payment_amount=payment_amount,
                payment_method=payment_method,
                payment_status=payment_status
            )
            payment.save()
            serializer = PaymentSerializer(payment, many=False)
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        except Order.DoesNotExist:
            return Response({'message': f'Order with ID {order_id} not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status= status.HTTP_500_INTERNAL_SERVER_ERROR)