from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView, Response
from django.db import transaction
from rest_framework import status
from products.models import Cart, Product, ProductCart, Order, OrderProduct
from products.serializers import ProductCartSerializer
from users.models import User


#add a new product to cart
class ProductCartCreateView(APIView):
    def post(self, request):
        cart_id = request.data.get("cart")
        products = request.data.get("products", [])


        # Validación de campos obligatorios
        if not cart_id or not products:
            return Response({"message": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            cart = Cart.objects.get(pk=cart_id)
        except Cart.DoesNotExist:
            return Response(
                {"message": "Cart not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            # Recuperar los productos en una sola consulta
            product_skus = [product["sku"] for product in products]
            products_db = Product.objects.filter(sku__in=product_skus)
            product_map = {product.sku: product for product in products_db}

            # Verificar que todos los SKUs sean válidos
            missing_skus = set(product_skus) - set(product_map.keys())
            if missing_skus:
                return Response(
                    {"message": f"Products not found for SKUs: {', '.join(missing_skus)}"},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # Crear ProductCart en una transacción atómica
            with transaction.atomic():
                product_carts = []
                for product_data in products:
                    sku = product_data["sku"]
                    quantity = product_data.get("quantity", 1)
                    product = product_map[sku]

                    product_cart = ProductCart.objects.create(
                        cart=cart, product=product, quantity=quantity
                    )
                    product_carts.append(product_cart)

                serializer = ProductCartSerializer(product_carts, many=True)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response(
                {"message": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        #handling exceptions
        except Cart.DoesNotExist:
            return Response({"message": f"Cart with ID {cart_id} doesn't exists."},
                                                                status = status.HTTP_400_BAD_REQUEST)

        except Product.DoesNotExist:
            return Response({"message": f"Product doesn't exists."}, status = status.HTTP_400_BAD_REQUEST)

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
            cart = Cart.objects.filter(name = cart_id, user = user).first()
            products = ProductCart.objects.filter(cart = cart)
            serializer = ProductCartSerializer(products, many = True)
            return Response(serializer.data, status.HTTP_200_OK)


        except User.DoesNotExist:
            return Response({"message": "User doesn't exists."}, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


#edit a product into a single cart
class ProductCartHasChanged(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        items = request.data.get("items", None)
        user = request.user

        if not items:
            return Response({'message': 'All fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            order = Order.objects.filter(user=user, status="PENDING").first()
            order_products = OrderProduct.objects.filter(order=order)  # Filtrar todos los productos de la orden
        except Order.DoesNotExist:
            return Response({'changed': True, 'message': 'No active order found'}, status=status.HTTP_200_OK)

        # Convertir los productos de la orden en un diccionario {product_id: quantity}
        order_product_map = {op.product.id: op.quantity for op in order_products}

        # Convertir los productos enviados en un diccionario {product_id: quantity}
        request_product_map = {item["id"]: item["quantity"] for item in items}

        # Comparar si las claves (productos) o los valores (cantidades) han cambiado
        if order_product_map != request_product_map:
            return Response({'changed': True}, status=status.HTTP_200_OK)

        return Response({'changed': False}, status=status.HTTP_200_OK)


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

