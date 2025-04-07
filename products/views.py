from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView, Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import LimitOffsetPagination
from .models import Category, Product, Coupon, UnitOfMeasure
from .permissions import AdminPermissions
from .serializers import (
    ProductSerializer, CouponSerializer, UnitOfMeasureSerializer,
)


class UnitOfMeasureView(APIView):
    """
    API view to perform CRUD operations on UnitOfMeasure.
    Only accessible to admin users.
    """
    permission_classes = [IsAdminUser]

    def get(self, request, unit_id=None):
        """
        Retrieve all units of measure or a specific one by ID.
        - If `unit_id` is provided, fetch a single unit.
        - Otherwise, return a list of all units.
        """
        try:
            if unit_id:
                # Fetch a single unit or return a 404 error if not found
                unit = get_object_or_404(UnitOfMeasure, id=unit_id)
                serializer = UnitOfMeasureSerializer(unit)
            else:
                # Fetch all units
                units = UnitOfMeasure.objects.all()
                serializer = UnitOfMeasureSerializer(units, many=True)

            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        """
        Create a new unit of measure.
        """
        serializer = UnitOfMeasureSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, unit_id):
        """
        Update an existing unit of measure.
        - Uses `partial=True` to allow partial updates.
        - Returns 404 if the unit is not found.
        """
        unit = get_object_or_404(UnitOfMeasure, id=unit_id)
        serializer = UnitOfMeasureSerializer(unit, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, unit_id):
        """
        Delete an existing unit of measure.
        - Returns 204 status if successful.
        - Returns 404 if the unit is not found.
        """
        unit = get_object_or_404(UnitOfMeasure, id=unit_id)
        unit.delete()
        return Response({"message": "Unit of measure successfully deleted"}, status=status.HTTP_204_NO_CONTENT)


#create a new product
class ProductCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    permission_classes = [IsAdminUser]
    def post(self, request):
        print(request.data)
        sku = request.data.get("sku", None)
        name = request.data.get("name", None)
        description = request.data.get("description", None)
        price = request.data.get("price", None)
        stock = request.data.get("stock", None)
        category = request.data.get("category_id", None)
        # check if all fields are fulfilled
        if not all([sku, name, description, price, stock, category]):
            return Response({"message": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if Product.objects.filter(sku=sku).exists():
                return Response({"message": f"Product with SKU {sku} already exists"},
                                status=status.HTTP_400_BAD_REQUEST)
            if Product.objects.filter(name = name).exists():
                return Response({"message": f"Product with name {name} already exists"},
                                status=status.HTTP_400_BAD_REQUEST)

            if not Category.objects.filter(pk=category).exists():
                return Response({"message": "Category does not exist!"}, status=status.HTTP_400_BAD_REQUEST)

            # Serialize and save the given product
            serializer = ProductSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response({"message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#retrieve all products
class ProductListView(APIView):
    def get(self, request):
        try:
            queryset = Product.objects.all()
            paginator = LimitOffsetPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            serializer = ProductSerializer(paginated_queryset, many= True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class RetrieveLatestProducts(ListAPIView):
    def get(self, request):
        try:
            queryset = Product.objects.filter(recommended=True)[:3]
            paginator = LimitOffsetPagination()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            serializer = ProductSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)



#retrieve all details of a single product
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
    permission_classes = [AdminPermissions]

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
        coupon_id = request.data.get("id", None)
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
            return Response({'message': f'Coupon code {coupon_code} not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)


class CouponCodeCheckView(APIView):
    """
    Validates a given discount coupon and returns the applicable discount.

    If the discount type is "FIXED", the function returns the total discount amount.
    If the discount type is "PERCENTAGE", it returns the percentage discount.

    Returns:
        dict: A dictionary containing:
            - 'discount' (str): The discount value (amount or percentage).
            - 'valid' (bool): Indicates whether the coupon is valid.
            - 'type' (str): Indicates the discount type
    """

    def post(self, request):
        coupon_code = request.data.get("coupon_code", None)
        if not coupon_code:
            return Response({'message': 'Coupon code is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            coupon = Coupon.objects.get(coupon_code=coupon_code)
            if coupon.is_valid():
                return Response({'valid': True, 'type':coupon.discount_type, 'discount': coupon.discount}, status=status.HTTP_200_OK)
            return Response({'valid': False, 'error': 'Cupón expirado o inactivo'}, status=status.HTTP_400_BAD_REQUEST)

        except Coupon.DoesNotExist:
            return Response({'message': f'Coupon code {coupon_code} not found!'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
