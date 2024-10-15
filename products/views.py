from rest_framework.views import APIView, Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Category, Product
from .serializers import (
    ProductSerializer,
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

                             
