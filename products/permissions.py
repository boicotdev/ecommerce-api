from rest_framework.permissions import IsAuthenticated, IsAdminUser

class AdminPermissions(IsAuthenticated, IsAdminUser):
    pass
