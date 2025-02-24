from rest_framework.views import APIView, Response
from rest_framework import status
import uuid

import mercadopago
from decouple import config
from users.models import User
from products.models import (
    Shipment,
    Payment, Order, OrderProduct, Product
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
        # Initialize the SDK with the access token
        mercado_pago = mercadopago.SDK(MP_ACCESS_TOKEN)
        items = request.data.get('items', [])

        preference_data = {
            'items': items,
            'back_urls': {
                'success': 'http://localhost:5173/payments/succes/',
                'failure': 'http://localhost:5173/payments/failure/',
                'pending': 'http://localhost:5173/payments/pending/',
            },
            'auto_return': 'approved',
        }

        # Create the payment preference
        preference_response = mercado_pago.preference().create(preference_data)
        if preference_response['status'] == 201:
            user = request.user
            order = Order.objects.create(user=user, status="PENDING")
            order.save()
            #set order products to Order instance
            for item in items:
                product = Product.objects.get(sku=item['sku'])
                order_product = OrderProduct.objects.create(order=order, product=product,
                                                            price=item['unit_price'], quantity=item['quantity'])
                order_product.save()
            return Response(preference_response['response'], status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': 'Error creating preference!'}, status=status.HTTP_400_BAD_REQUEST)


class MercadoPagoPaymentView(APIView):
    def post(self, request, *args, **kwargs):
        # Inicializa el SDK de MercadoPago con el token de acceso
        sdk = mercadopago.SDK(MP_ACCESS_TOKEN)

        # Configura opciones de idempotencia (opcional)
        request_options = mercadopago.config.RequestOptions()
        request_options.custom_headers = {
            'x-idempotency-key': request.data.get('idempotency_key', str(uuid.uuid4()))
        }

        try:
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

            #print("------------------------- request data --------------------------")
            #print(request.data)
        except (TypeError, ValueError) as e:
            return Response(
                {"error": "Invalid payment data", "details": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Crea el pago usando la API de MercadoPago
        try:
            payment_response = sdk.payment().create(request.data, request_options)
            payment = payment_response.get("response", {})
            return Response(payment, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {"error": "Payment creation failed", "details": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

#cart details
class PaymentDetailsViewView(APIView):
    def get(self, request):
        payment_id = request.query_params.get("payment", None)
        if not  payment_id:
            return Response({'message': 'Payment ID is required'}, status = status.HTTP_400_BAD_REQUEST)
        try:
            payment = Payment.objects.get(pk = payment_id)
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
        order_id = request.data.get('order_id', None)
        payment_amount = request.data.get('payment_amount', None)
        payment_method = request.data.get('payment_method', None)
        payment_status = request.data.get('payment_status', None)
        payment_date = request.data.get('payment_date', None)
        print(request.data)

        if not all([order_id, payment_date, payment_amount, payment_method, payment_status]):
            return Response({'message': 'All fields are required'}, status = status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(id=order_id)
            #order.status = "DELIVERED" #change the order status
            #order.save()
            payment = Payment.objects.create(order_id=30, payment_date=payment_date, payment_amount=payment_amount,
                                             payment_method=payment_method, payment_status=payment_status)
            payment.save()
            serializer = PaymentSerializer(payment, many=False)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'message': f'Order with ID {order_id} not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status= status.HTTP_500_INTERNAL_SERVER_ERROR)