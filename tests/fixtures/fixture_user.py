import pytest


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(username='TestUser',
                                                 password='QweCxz88005553535',
                                                 first_name="Testuser",
                                                 last_name="Пупкин",
                                                 email="test@yandex.ru",
                                                 birth_date="2023-04-29")


@pytest.fixture
def user_2(django_user_model):
    return django_user_model.objects.create_user(username='TestUser_2',
                                                 password='QweCxz88005553535',
                                                 first_name="Testuser2",
                                                 last_name="Пупкин",
                                                 email="test_2@yandex.ru",
                                                 birth_date="2023-04-29")


@pytest.fixture
def another_user(django_user_model):
    return django_user_model.objects.create_user(username='TestUserAnother',
                                                 password='QweCxz88005553535',
                                                 first_name="Testuser",
                                                 last_name="Пупкин",
                                                 email="anothertest@yandex.ru",
                                                 birth_date="2023-04-29")


@pytest.fixture
def token(user):
    from rest_framework.authtoken.models import Token
    token, created = Token.objects.get_or_create(user=user)

    return token.key


@pytest.fixture
def user_client(token):
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    return client
