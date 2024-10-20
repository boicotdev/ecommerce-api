from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User




class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    We're using rest_framework_simplejwt to handle authentications
    We're using email field to user identificate
      - params: {"email": "user email", "password": "user password"}
      - returns: {"access": "an access token", "refresh": "a refresh access token"}
      
    """
    def validate(self, attrs):
        data = super().validate(attrs)
        data['id'] = self.user.id
        data['is_superuser'] = self.user.is_superuser
        data['username'] = self.user.username
        data['avatar'] = self.user.avatar.url
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", 'username', 'email', 'password',
                  'first_name', 'last_name', 'avatar', 'phone', 'address', 'rol', 'date_joined', 'is_staff', 'is_superuser']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        # Extraer datos del campo groups
        groups_data = validated_data.pop('groups', [])

        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()

        # Agregar los grupos después de guardar el usuario
        for group_data in groups_data:
            instance.groups.add(group_data)

        return instance

