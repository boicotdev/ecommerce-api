from rest_framework.views import APIView, Response
from rest_framework import status
from products.models import  Cart, Product, ProductCart
from products.serializers import ProductCartSerializer
from users.models import User


#add a new product to cart
class ProductCartCreateView(APIView):
    def post(self, request):
        cart_id = request.data.get("cart", None)
        product_id = request.data.get("product", None)
        product_quantity = request.data.get("quantity", None)

        #check if required fields are fulfilled
        if not cart_id or not product_id or not product_quantity:
            return Response({"message": "All fields are required"}, status = status.HTTP_400_BAD_REQUEST)

        try:
            cart = Cart.objects.get(pk = cart_id)
            product = Product.objects.get(pk = product_id)
            serializer = ProductCartSerializer(data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status = status.HTTP_201_CREATED)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        #handling exceptions
        except Cart.DoesNotExist:
            return Response({"message": f"Cart with ID {cart_id} doesn't exists."},
                                                                status = status.HTTP_400_BAD_REQUEST)

        except Product.DoesNotExist:
            return Response({"message": f"Product with ID {product_id} doesn't exists."},
                                                                status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_400_BAD_REQUEST)

#retrieve all product carts pre user
class ProductCartUserList(APIView):
    def get(self, request):
        cart_id = request.query_params.get("cart", None)
        user_id = request.query_params.get("user", None)

        if not cart_id or not user_id:
            return Response({"message": "Cart ID wasn't provided."}, status = status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk = user_id)
            cart = Cart.objects.filter(pk = cart_id, user = user).first()
            products = ProductCart.objects.filter(cart = cart)
            serializer = ProductCartSerializer(products, many = True)
            print(products)
            return Response(serializer.data, status.HTTP_200_OK)


        except User.DoesNotExist:
            return Response({"message": "User doesn't exists."}, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

#edit a product into a single cart

#remove a product into a cart
class ProductCartUserRemove(APIView):
    def delete(self, request):
        cart_id = request.data.get("cart", None)
        product_id = request.data.get("product", None)
        user_id = request.data.get("user", None)

        if not cart_id or not product_id or not user_id:
            return Response({"message": "All fields are required"}, status = status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk = user_id)
            cart = Cart.objects.filter(pk = cart_id, user = user).first()
            product = ProductCart.objects.filter(pk = product_id, cart = cart).first()

            #check if Cart or ProductCart not exists
            if not cart:
                raise Cart.DoesNotExist
            if not  product:
                raise ProductCart.DoesNotExist

            #deleting a product
            product.delete()
            return Response({"message": "Product cart was deleted successfully"}, status = status.HTTP_204_NO_CONTENT)

        except User.DoesNotExist:
            return Response({"message": f"User with ID {user_id} doesn't exists"}, status = status.HTTP_400_BAD_REQUEST)

        except Cart.DoesNotExist:
            return Response({"message": f"Cart with ID {cart_id} doesn't exists"}, status = status.HTTP_400_BAD_REQUEST)

        except ProductCart.DoesNotExist:
            return Response({"message": f"Product with ID {product_id} doesn't exists"}, status = status.HTTP_400_BAD_REQUEST)


        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

