from rest_framework.views import APIView, Response
from rest_framework import status
from rest_framework.decorators import api_view
import mercadopago
from decouple import config
from users.models import User
from products.models import (
    Shipment,
    Payment, Order
)
from products.serializers import (
    ShipmentSerializer,
    PaymentSerializer
)
import uuid

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
        # Inicializar el SDK con el access token
        mercado_pago = mercadopago.SDK(MP_ACCESS_TOKEN)

        items = request.data.get('items', [])

        preference_data = {
            'items': items,
            'back_urls': {
                'success': 'http://localhost:5172/payments/succes/',
                'failure': 'http://localhost:5172/payments/failure/',
                'pending': 'http://localhost:5172/payments/pending/',
            },
            'auto_return': 'approved',
        }

        # Crear la preferencia de pago
        preference_response = mercado_pago.preference().create(preference_data)
        if preference_response['status'] == 201:
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
            #print(payment_data)
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

