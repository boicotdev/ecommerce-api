from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.views import APIView, Response
from rest_framework import status
from products.models import Order, OrderProduct, Payment
from users.models import User
from products.serializers import OrderSerializer

#create
class OrderCreateView(APIView):
    def post(self, request):
        check_status_list = ["PENDING", "DELIVERED", "CANCELLED", "APPROVED"]
        status_order = request.data.get("status", None)
        user_id = request.data.get("user", None)['id']

        #check if required fields are fulfilled
        if not user_id or not status_order:
            return Response({"message": "All fields are required"}, status = status.HTTP_400_BAD_REQUEST)
        #check if the given status is valid
        if not status_order in check_status_list:
            return Response({"message": f"The given status {status_order} isn't valid"}, status = status.HTTP_400_BAD_REQUEST)

        try:
            serializer = OrderSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save(user=User.objects.get(pk=user_id))
                return Response(serializer.data, status = status.HTTP_201_CREATED)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

#read all orders of a single user
class OrderUserList(APIView):
    def get(self, request):
        user_id = request.query_params.get("user", None)
        
        if not user_id:
            return Response({"message": "User ID is required"}, status = status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk = user_id)
            orders = Order.objects.filter(user = user)
            serializer = OrderSerializer(orders, many = True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status = status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderUserCancelView(APIView):
    def put(self, request):
        order_id = request.data.get("order")
        user_id = request.data.get("user")
        new_status = request.data.get("status")

        if not order_id or not user_id or not new_status:
            return Response({"message": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        # Buscar la orden que pertenezca al usuario
        order = Order.objects.filter(pk=order_id, user_id=user_id).first()

        if not order:
            return Response({"message": "Order not found or does not belong to user"}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si la orden tiene un pago asociado
        has_payment = Payment.objects.filter(order=order).exists()

        # Definir los estados en los que se puede cancelar la orden
        cancelable_status = {"PENDING", "ON_HOLD"}
        if has_payment:
            cancelable_status.update({"PENDING", "FAILED"})

        if order.status not in cancelable_status:
            return Response({"message": f"No se puede cancelar en este estado {order.status}"}, status=status.HTTP_400_BAD_REQUEST)

        # Actualizar el estado de la orden a CANCELLED
        serializer = OrderSerializer(order, data={"status": "CANCELLED"}, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

#delete
class OrderUserRemove(APIView):
    def delete(self, request):
        order_id = request.data.get("order")
        user_id = request.data.get("user")

        if not order_id or not user_id:
            return Response({"message": "All fields are required"}, status = status.HTTP_200_OK)
        try:
            user = User.objects.get(pk = user_id)
            order = Order.objects.filter(user = user, pk = order_id)
            order.delete()
        
            return Response({"message": "Order deleted successfully"}, status = status.HTTP_204_NO_CONTENT)
        
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status = status.HTTP_400_BAD_REQUEST)
        
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status = status.HTTP_400_BAD_REQUEST)
        

        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

#order list with superuser permissions
class OrdersDashboardView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request):
        try:
            orders = Order.objects.all()
            serializer = OrderSerializer(orders, many = True)
            return Response(serializer.data, status = status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class OrderDashboardDetailsView(APIView):
    #permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        order_id = request.query_params.get("order", None)
        if not order_id:
            return Response({"message": "Order ID is required"}, status = status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(pk = order_id)
            serializer = OrderSerializer(order, many = False).data
            return Response(serializer, status = status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status= status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": str(e)}, status= status.HTTP_500_INTERNAL_SERVER_ERROR)













