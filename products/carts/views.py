from rest_framework.views import APIView, Response
from rest_framework import status
from products.models import Cart, Product
from users.models import User
from products.serializers import  (
    CartSerializer,
    ProductCartSerializer
)


#create order
class CartCreateView(APIView):
    def post(self, request):
        user = request.data.get("user", None)
        name = request.data.get("name", None)
        description = request.data.get("description", None)
        print(request.data)

        if not user or not name or not description:
            return Response({"message": "All fields are required!"}, status = status.HTTP_400_BAD_REQUEST)

        #check if given order name already exists
        try:
            cart = Cart.objects.get(name = name)
            if cart:
                return Response({"message": f"Cart with name {name} already exists!"})
        except Cart.DoesNotExist:
            serializer = CartSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status = status.HTTP_201_CREATED)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class CartItemCreateView(APIView):
    def post(self, request):
        data = request.data.get("data", None)
        cart_id = data['cart_id']
        cart_items = data['items']
        try:
            cart = Cart.objects.get(name=cart_id)
            serializer = ProductCartSerializer(data=cart_items, context={'cart': cart}, many=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Cart.DoesNotExist:
            return Response({'message': f'Cart with name {cart_id} does not exists'}, status= status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': str(e)}, status= status.HTTP_500_INTERNAL_SERVER_ERROR)

#retrieve carts per user
class CartUserListView(APIView):
    def get(self, request):
        user_id = request.query_params.get("user", None)
        if not user_id:
            return Response({"message": "User field are required"}, status = status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(pk = user_id)
            carts = Cart.objects.filter(user__id = user.id)
            serializer = CartSerializer(carts, many=True)
            return Response(data=serializer.data, status = status.HTTP_200_OK)

        except Cart.DoesNotExist:
            return Response({"message": f"Carts with {user} not exists."},
                                                    status = status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"message": f"User with {user_id} not exists."},
                            status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


#delete cart
class CartUserDelete(APIView):
    def delete(self, request):
        user_id = request.data.get("user", None)
        cart_name = request.data.get("name", None)
        if not user_id or not cart_name:
            return Response({"message": "User ID is required"}, status = status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(pk = user_id)
            cart = Cart.objects.get(user = user, name = cart_name)
            cart.delete()
            return Response({"message": "Cart was deleted successfully."}, status = status.HTTP_204_NO_CONTENT)

        except Cart.DoesNotExist:
            return Response({"message": f"Cart with name {cart_name} not exists."}, status = status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response({"message": f"User with {user_id} not exists."}, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": "Cart was deleted successfully."}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

