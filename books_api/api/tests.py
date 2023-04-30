import pytest
from rest_framework.test import APIClient
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.authtoken.models import Token

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user():
    return User.objects.create_user(
        username='test_user',
        password='test_password'
    )

@pytest.fixture
def token(user):
    return Token.objects.create(user=user)

