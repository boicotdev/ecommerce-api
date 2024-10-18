from rest_framework.views import APIView, Response
from rest_framework import status
from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from rest_framework_simplejwt.views import  TokenObtainPairView, TokenRefreshView
from .models import User



#login view
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer



#create a new User instance
class UserCreateView(APIView):
    """
    Create a new `User`
    """
    def post(self, request):
        username = request.data.get("username", None)
        first_name = request.data.get("first_name", None)
        last_name = request.data.get("last_name", None)
        email = request.data.get("email", None)

        #validate if required fields are fulfilled
        if not username or not first_name or not last_name or not email:
            return Response({"message": "Some fields are missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if User.objects.filter(email = email).exists():
                return Response({"message": f"User with {email} already exists!"}, status = status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(username = username).exists():
                return Response({"message": f"User with {username} already exists!"}, status = status.HTTP_400_BAD_REQUEST)

            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status = status.HTTP_201_CREATED)
            return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

#update a single user
class UserUpdateView(APIView):
    def put(self, request):
        username = request.data.get("username", None)

        if not username:
            return Response({"message": "Username field is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if User.objects.filter(username=username).exists():
                user_instance = User.objects.get(username=username)
                # Pasar el usuario existente al serializador para su actualización
                user_serializer = UserSerializer(user_instance, data=request.data, partial=True)

                if user_serializer.is_valid():
                    user_serializer.save()  # Guardar los cambios
                    return Response(user_serializer.data, status=status.HTTP_200_OK)

                return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"message": "Internal server error!"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#retrieve all users
class UserListView(APIView):
    """
    List all users into the database
    """

    def get(self, request):
        users = User.objects.all()
        data = UserSerializer(users, many=True)
        return Response(data.data, status = status.HTTP_200_OK)

#remove a single user
class UserDeleteView(APIView):
    def delete(self, request):
        username = request.data.get("username", None)
        if not username:
            return Response({"message": "Username field is required!"}, status = status.HTTP_400_BAD_REQUEST)
        try:
            user = User.objects.get(username = username)
            if user:
                user.delete()
                return Response({"message": "User was deleted successfully"}, status = status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"message": str(e)}, status = status.HTTP_500_INTERNAL_SERVER_ERROR)

