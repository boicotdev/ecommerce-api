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

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import mercadopago

class CreatePaymentPreference(APIView):
    def post(self, request):
        # Inicializar el SDK con el access token
        mercado_pago = mercadopago.SDK(MP_ACCESS_TOKEN)

        items = request.data.get('items', [])

        preference_data = {
            'items': items,
            'back_urls': {
                'success': 'http://127.0.0.1:8000/api/v1/payments/succes/',
                'failure': 'http://127.0.0.1:8000/api/v1/payments/failure/',
                'pending': 'http://127.0.0.1:8000/api/v1/payments/pending/',
            },
            'auto_return': 'approved',
        }

        # Crear la preferencia de pago
        preference_response = mercado_pago.preference().create(preference_data)
        if preference_response['status'] == 201:
            return Response(preference_response['response'], status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': 'Error creating preference!'}, status=status.HTTP_400_BAD_REQUEST)


