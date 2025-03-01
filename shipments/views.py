from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response

from products.models import Shipment
from products.serializers import ShipmentSerializer


class ShipmentCreateView(APIView):
    permission_classes = [IsAuthenticated]
    """
    Handle all operations related to create a shipment order
    """

    def post(self, request):
        print(request.data)
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


class ShipmentListView(APIView):
    """
    Retrieve all shipments into the ecommerce
    Superuser permissions are required to access this view
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            shipments = Shipment.objects.all()
            serializer = ShipmentSerializer(shipments, many=True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class ShipmentUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    """
    Update a single `Shipment` object, special permissions are required to access this view
    """
    def put(self, request):
        shipment_id = request.data.get("shipment", None)
        if not shipment_id:
            return Response({'message': 'Shipment ID is missing, try again.'}, status = status.HTTP_400_BAD_REQUEST)

        try:
            shipment = Shipment.objects.get(pk=shipment_id)
            serializer = ShipmentSerializer(shipment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status = status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Shipment.DoesNotExist:
            return Response({'message': f'Shipment with the given ID was\'nt found!'}, status = status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'message': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)