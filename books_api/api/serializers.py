from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
import django.contrib.auth.password_validation as validators

from books.models import Book

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name',
                  'last_name', 'birth_date')


class TokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label='Email',
        write_only=True)
    password = serializers.CharField(
        label='Пароль',
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True)
    token = serializers.CharField(
        label='Токен',
        read_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email=email)
                if not authenticate(username=user.username, password=password):
                    raise serializers.ValidationError(
                        'Пароль не верный или Вы не указали пользователя или ',
                        code='authorization')
            else:
                raise serializers.ValidationError(
                        'Пользователя с таким email нет',
                        code='authorization')
        else:
            msg = 'Необходимо указать "адрес электронной почты" и "пароль".'
            raise serializers.ValidationError(
                msg,
                code='authorization')
        attrs['user'] = user
        return attrs


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name',
            'birth_date'
            )

    def validate_password(self, password):
        validators.validate_password(password)
        return password


class UserPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        label='Новый пароль')
    current_password = serializers.CharField(
        label='Текущий пароль')

    def validate_current_password(self, current_password):
        user = self.context['request'].user
        if not authenticate(
                username=user.username,
                password=current_password):
            raise serializers.ValidationError(
                "Не удается авторизоваться", code='authorization')
        return current_password

    def validate_new_password(self, new_password):
        validators.validate_password(new_password)
        return new_password

    def create(self, validated_data):
        user = self.context['request'].user
        password = make_password(
            validated_data.get('new_password'))
        user.password = password
        user.save()
        return validated_data


class BookSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Book
