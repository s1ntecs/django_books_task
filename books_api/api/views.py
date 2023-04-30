from djoser.views import UserViewSet
from datetime import datetime

from django.shortcuts import get_object_or_404
from django.contrib.auth.hashers import make_password
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token

from rest_framework import viewsets, filters, status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view
from rest_framework.response import Response
from books.models import Book
from .serializers import (BookSerializer, UserCreateSerializer,
                          UserPasswordSerializer, TokenSerializer,
                          UserSerializer)
from .permissions import IsOwnerOrReadOnly
from users.models import User


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        recipe = Book.objects.all().order_by('id')
        return recipe

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        publication_date = datetime.now()
        serializer.save(publication_date=publication_date)


class UsersViewSet(UserViewSet):
    """Пользователи."""

    queryset = User.objects.all()
    lookup_field = 'username'
    filter_backends = (filters.OrderingFilter, filters.SearchFilter,)
    ordering = ['username']
    search_fields = ['username']

    def get_serializer_class(self):
        if self.request.method.lower() == 'post':
            return UserCreateSerializer
        return UserSerializer

    def get_object(self):
        id = self.kwargs.get('username')
        user = get_object_or_404(User, id=id)
        return user

    def perform_create(self, serializer):
        password = make_password(self.request.data['password'])
        serializer.save(password=password)


class AuthToken(ObtainAuthToken):
    """Авторизация пользователя."""

    serializer_class = TokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'auth_token': token.key},
            status=status.HTTP_201_CREATED)


@api_view(['post'])
def set_password(request):
    """Изменить пароль."""

    serializer = UserPasswordSerializer(
        data=request.data,
        context={'request': request})
    serializer.is_valid(raise_exception=True)
    if serializer.is_valid():
        serializer.save()
        return Response(
            {'message': 'Пароль изменен!'},
            status=status.HTTP_201_CREATED)
    return Response(
        {'error': 'Введите верные данные!'},
        status=status.HTTP_400_BAD_REQUEST)
