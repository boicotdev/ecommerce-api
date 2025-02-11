from rest_framework.views import APIView, Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import Category, Product, Coupon
from .permissions import AdminPermissions
from .serializers import (
    ProductSerializer, CouponSerializer,
)


#create a new product
class ProductCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    #permission_classes = [IsAuthenticated, IsAdminUser]
    def post(self, request):
        sku = request.data.get("sku", None)
        name = request.data.get("name", None)
        description = request.data.get("description", None)
        price = request.data.get("price", None)
        stock = request.data.get("stock", None)
        category = request.data.get("category_id", None)
        print(request.data)
        # check if all fields are fulfilled
        if not all([sku, name, description, price, stock, category]):
            return Response({"message": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if Product.objects.filter(sku=sku).exists():
                print("filtro de sku error")
                return Response({"message": f"Product with SKU {sku} already exists"},
                                status=status.HTTP_400_BAD_REQUEST)
            if Product.objects.filter(name = name).exists():
                print("product exist")
                return Response({"message": f"Product with name {name} already exists"},
                                status=status.HTTP_400_BAD_REQUEST)

            if not Category.objects.filter(pk=category).exists():
                print("no exist category")
                return Response({"message": "Category does not exist!"}, status=status.HTTP_400_BAD_REQUEST)

            # Serialize and save the given product
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(str(e))
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#retrieve all products
class ProductListView(APIView):
    def get(self, request):
        try:
            products = Product.objects.all()
            serializer = ProductSerializer(products, many= True)
            return Response(serializer.data, status = status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


#retrieve a single product 
class ProductDetailsView(APIView):
    def get(self, request):
        sku = request.query_params.get("sku", None)
        
        if not sku:
            return Response({"message":"Sku is required"}, status = status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.get(sku = sku)
            serializer = ProductSerializer(product)
            return Response(serializer.data, status = status.HTTP_200_OK)

        except Product.DoesNotExist:
            return Response({"message": f"Product with SKU {sku}"}, status = status.HTTP_400_BAD_REQUEST)
            

        except Exception as e:
            return Response({"message" : str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


#update a single product
class ProductUpdateView(APIView):
    #permission_classes = [IsAuthenticated, IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def put(self, request):
        product_sku = request.data.get("sku")

        if not product_sku:
            return Response({"message" : f"Product with ID {product_sku} doesn't exists"}, status = status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(sku = product_sku)
            serializer = ProductSerializer(product, data = request.data, partial = True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status = status.HTTP_200_OK)
            
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        
        except Product.DoesNotExist:
            return Response({"message" : f"Product with SKU {product_sku} doesn't exists"}, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message" : str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


#remove a single product
class ProductRemoveView(APIView):
    def delete(self, request):
        #permission_classes = [IsAuthenticated, IsAdminUser]
        product_sku = request.data.get("sku", None)

        if not product_sku:
            return Response({"message":"Product ID is required."}, status = status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(sku = product_sku)
            product.delete()
            return Response({"message" : "Product was deleted successfully"}, status = status.HTTP_204_NO_CONTENT)

        except Product.DoesNotExist:
            return Response({"message" : f"Product with ID {product_sku} doesn't exists"}, status = status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"message" : str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class CouponsCreateView(APIView):
    permission_classes = [AdminPermissions]
    def post(self, request):
        print(request.data)
        coupon_code = request.data.get('coupon_code', None)
        discount = request.data.get('discount', None)
        discount_type = request.data.get('discount_type', None)
        expiration_date = request.data.get('expiration_date', None)

        if not  coupon_code or not discount or not discount_type or not expiration_date:
            return Response({'message': 'Todos los campos son obligatorios'}, status = status.HTTP_400_BAD_REQUEST)

        try:
            serializer = CouponSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status = status.HTTP_201_CREATED)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CouponsAdminRetrieveView(APIView):
    """
    Only admin user can access
    - Retrieve all coupons available
    """
    #permission_classes = [AdminPermissions]

    def get(self, request):
        try:
            coupons = Coupon.objects.all()
            coupons_serializer = CouponSerializer(coupons, many= True)
            return Response(coupons_serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class CouponUpdateView(APIView):
    permission_classes = [AdminPermissions]
    def put(self, request):
        coupon_id = request.data.get("coupon_id", None)
        print(request.data)
        if not coupon_id:
            return Response({'message': 'Coupon ID is required'}, status = status.HTTP_400_BAD_REQUEST)
        try:
            coupon = Coupon.objects.get(pk = coupon_id)
            serializer = CouponSerializer(coupon, data= request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status = status.HTTP_200_OK)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

        except Coupon.DoesNotExist:
            return Response({'message': f'Coupon ID {coupon_id} not found!'})
        except Exception as e:
            return Response({'message': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class CouponDeleteView(APIView):
    permission_classes = [AdminPermissions]
    def post(self, request):
        coupon_code = request.data.get("coupon_code", None)

        if not coupon_code:
            return Response({'message': 'Coupon code is required'}, status = status.HTTP_400_BAD_REQUEST)
        try:
            coupon = Coupon.objects.get(coupon_code = coupon_code)
            coupon.delete()
            return Response({'message': f'Coupon deleted successfully.'}, status = status.HTTP_204_NO_CONTENT)

        except Coupon.DoesNotExist:
            return Response({'message': f'Coupon code {coupon_code} not found!'})
        except Exception as e:
            return Response({'message': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


#check if a given coupon code is valid
class CouponCodeCheckView(APIView):
    """
    pass
    """
    def post(self, request):
        coupon_code = request.data.get("coupon_code", None)

        if not coupon_code:
            return Response({'message': 'Coupon code is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            coupon = Coupon.objects.get(coupon_code=coupon_code)
            coupon.delete()
            return Response({'message': f'Coupon deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

        except Coupon.DoesNotExist:
            return Response({'message': f'Coupon code {coupon_code} not found!'})
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)