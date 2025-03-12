from itertools import product

from rest_framework.views import APIView, Response
from rest_framework import status
from products.models import OrderProduct, Order, Product
from products.serializers import OrderProductSerializer


#create
class OrderProductCreateView(APIView):
    def post(self, request):
        order_id = request.data.get("order", None)
        product_id = request.data.get("product", None)
        product_price = request.data.get("price", None)
        product_quantity = request.data.get("price", None)

        if not order_id or not product_id or not product_price or not product_quantity:
            return Response({"message": "All fields are required!"}, status = status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.get(pk = order_id)
            product = Product.objects.get(pk = product_id)
            serializer = OrderProductSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status = status.HTTP_201_CREATED)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        #handling exceptions
        except Product.DoesNotExist:
            return Response({"message": "Product doesn't exists!"}, status = status.HTTP_400_BAD_REQUEST)

        except Order.DoesNotExist:
            return Response({"message": "Order doesn't exists!"}, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

#read

#update

#delete
