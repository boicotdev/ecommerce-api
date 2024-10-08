from multiprocessing.managers import Value
from unicodedata import category

from rest_framework.views import APIView, Response
from rest_framework import status
from .models import Category, Product
from .serializers import (
    ProductSerializer,
    CategorySerializer,
    CartSerializer,
    ProductCartSerializer,
    OrderSerializer,
    OrderProductSerializer
)

#create a new category
class CategoryCreateView(APIView):
    def post(self, request):
        category_name = request.data.get("name", None)
        if not category_name:
            return Response({"message": "Category name is required"}, status = status.HTTP_400_BAD_REQUEST)
        try:
            if Category.objects.filter(name = category_name).exists():
                return Response({"message": f"Category with name {category_name} already exists!"})
            serializer = CategorySerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status = status.HTTP_201_CREATED)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

#create a new product
class ProductCreateView(APIView):
    def post(self, request):
        sku = request.data.get("sku", None)
        name = request.data.get("name", None)
        description = request.data.get("description", None)
        price = request.data.get("price", None)
        stock = request.data.get("stock", None)
        category = request.data.get("category", None)

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

