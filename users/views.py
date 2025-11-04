from django.shortcuts import render
from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API for seen users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer