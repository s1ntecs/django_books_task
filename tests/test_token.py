import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


class TestToken:
    create_user = '/api/users/'
    url_create = '/api/auth/token/login/'
    url_refresh = '/api/auth/token/refresh/'
    token = None

    @pytest.fixture
    def api_client(self):
        return APIClient()

    @pytest.mark.django_db(transaction=True)
    def test_user_create_request_data(self, api_client):
        valid_data = {
            'username': 'new_user',
            'password': 'QweCxz88005553535',
            'first_name': 'new_user',
            'last_name': 'Ivanov',
            'email': 'new_user@yandex.ru',
            'birth_date': '1993-04-29'
        }
        response = api_client.post(self.create_user, data=valid_data)
        code_expected = 201
        resp_user = response.json()
        assert response.status_code == code_expected
        assert User.objects.filter(email=valid_data['email']).exists()
        test_user = User.objects.filter(email="new_user@yandex.ru").first()
        assert 'id' in resp_user, (
            'Проверьте, что добавили `id` сериализатора модели User'
        )
        assert 'email' in resp_user, (
            'Проверьте, что добавили `email` сериализатора модели User'
        )
        assert 'username' in resp_user, (
            'Проверьте, что добавили `username` сериализатора модели User'
        )
        assert 'first_name' in resp_user, (
            'Проверьте, что добавили `first_name` сериализатора модели User'
        )
        assert 'last_name' in resp_user, (
            'Проверьте, что `last_name` сериализатора модели User возвращает фамилию'
        )
        assert 'birth_date' in resp_user, (
            'Проверьте, что `last_name` сериализатора модели User возвращает фамилию'
        )
        assert test_user.username == 'new_user', (
            'Проверьте, что при создании User данные username правильно введены'
        )
        assert test_user.email == 'new_user@yandex.ru', (
            'Проверьте, что при создании User данные email правильно введены'
        )
        assert test_user.first_name == 'new_user', (
            'Проверьте, что при создании User данные first_name правильно введены'
        )
        assert test_user.last_name == 'Ivanov', (
            'Проверьте, что при создании User данные last_name правильно введены'
        )
        assert str(test_user.birth_date) == "1993-04-29", (
            'Проверьте, что при создании User данные birth_date правильно введены'
        )

    @pytest.mark.django_db(transaction=True)
    def test_token_create__invalid_request_data(self, api_client, user):
        url = self.url_create
        response = api_client.post(url)
        code_expected = 400
        assert response.status_code == 400, (
            f'Убедитесь, что при запросе `{url}` без параметров, '
            f'возвращается код {code_expected}'
        )
        fields_invalid = ['email', 'password']
        for field in fields_invalid:
            assert field in response.json().keys(), (
                f'Убедитесь, что при запросе `{url}` без параметров, '
                f'возвращается код {code_expected} с сообщением о том, '
                'при обработке каких полей возникла ошибка.'
                f'Не найдено поле {field}'
            )

        username_invalid = 'invalid_username_not_exists'
        password_invalid = 'invalid pwd'
        data_invalid = {
            'username': username_invalid,
            'password': password_invalid
        }
        response = api_client.post(url, data=data_invalid)
        code_expected = 400

        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе `{url}` без параметров, '
            f'возвращается код {code_expected}'
        )
        username_valid = user.email
        data_invalid = {
            'email': username_valid,
            'password': password_invalid
        }
        response = api_client.post(url, data=data_invalid)
        assert response.status_code == code_expected, (
            f'Убедитесь, что при запросе `{url}` без параметров, '
            f'возвращается код {code_expected}'
        )
        field = 'non_field_errors'
        assert field in response.json(), (
            f'Убедитесь, что при запросе `{url}` с некорректным password, '
            f'возвращается код {code_expected} с соответствующим сообщением '
            f'в поле {field}'
        )

    @pytest.mark.django_db(transaction=True)
    def test_token_create__valid_request_data(self, api_client, user):
        url = self.url_create
        valid_data = {
            'email': user.email,
            'password': 'QweCxz88005553535'
        }
        response = api_client.post(url, data=valid_data)
        code_expected = 201

        assert response.status_code == code_expected
        assert 'auth_token' in response.data
        assert response.data['auth_token'] is not None
        print(response.data['auth_token'])
        self.token = response.data['auth_token']

    @pytest.mark.django_db(transaction=True)
    def test_user_patch(self, api_client, user):
        url = self.url_create
        valid_data = {
            'email': user.email,
            'password': 'QweCxz88005553535'
        }
        response = api_client.post(url, data=valid_data)
        api_client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['auth_token'])
        patch_data = {
            'username': 'new_username',
            'first_name': 'new_first_name',
            'last_name': 'new_last_name',
            'email': 'new_email@yandex.ru',
            'birth_date': '1995-05-15'
        }
        response = api_client.patch(f'/api/users/{user.id}/', data=patch_data)
        assert response.status_code == 200, (
            'Проверьте, что при PATCH запросе `/api/users/{id}/` возвращаете статус 200'
        )

        test_user = User.objects.filter(id=user.id).first()

        assert test_user, (
            'Проверьте, что при PATCH запросе `/api/users/{id}/` вы не удалили пользователя'
        )

        assert test_user.username == 'new_username', (
            'Проверьте, что при PATCH запросе `/api/users/{id}/` вы изменяете username'
        )

        assert test_user.first_name == 'new_first_name', (
            'Проверьте, что при PATCH запросе `/api/users/{id}/` вы изменяете first_name'
        )

        assert test_user.last_name == 'new_last_name', (
            'Проверьте, что при PATCH запросе `/api/users/{id}/` вы изменяете last_name'
        )

        assert test_user.email == 'new_email@yandex.ru', (
            'Проверьте, что при PATCH запросе `/api/users/{id}/` вы изменяете email'
        )

        assert str(test_user.birth_date) == "1995-05-15", (
            'Проверьте, что при PATCH запросе `/api/users/{id}/` вы изменяете birth_date'
        )
