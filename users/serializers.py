from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password',
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


class AdminRegisterUserViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password',
                  'first_name', 'last_name', 'avatar', 'phone', 'address', 'rol', 'is_staff', 'date_joined', 'is_superuser']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        groups_data = validated_data.pop('groups', [])

        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()

        # Agregar los grupos después de guardar el usuario
        for group_data in groups_data:
            instance.groups.add(group_data)

        return instance


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['id'] = self.user.id
        data['is_superuser'] = self.user.is_superuser
        data['username'] = self.user.username
        return data