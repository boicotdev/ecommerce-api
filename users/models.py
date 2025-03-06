from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from django.contrib.auth.models import Group, Permission


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Please provide an email address')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username=username, email=email, password=password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(
        default='static/images/users/avatar.jpg',
        upload_to='static/images/users/', blank=True, null=True)
    address = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True)
    rol = models.CharField(max_length=15)
    # Evitar conflictos en groups y user_permissions
    groups = models.ManyToManyField(Group, related_name='custom_user_set')
    user_permissions = models.ManyToManyField(Permission, related_name='custom_user_permissions_set')
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', ]

    objects = CustomUserManager()

    def __str__(self) -> str:
        return f'{self.username}'


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "User comments+")
    raw_comment = models.TextField(max_length = 1000)
    pub_date = models.DateTimeField(auto_now_add = True)
    
    def __str__(self):
        return f"Comentario del usuario {self.user.username} | publicado {self.pub_date}"
