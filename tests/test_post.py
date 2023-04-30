import pytest

from books.models import Book


class TestPostAPI:

    @pytest.mark.django_db(transaction=True)
    def test_post_not_found(self, client, book):
        response = client.get('/api/books/')

        assert response.status_code != 404, (
            'Страница `/api/books/` не найдена, проверьте этот адрес в *urls.py*'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_list_not_auth(self, client, book):
        response = client.get('/api/books/')

        assert response.status_code == 200, (
            'Проверьте, что на `/api/books/` при запросе без токена возвращаете статус 200'
        )

    @pytest.mark.django_db(transaction=True)
    def test_post_single_not_auth(self, client, book):
        response = client.get(f'/api/books/{book.id}/')

        assert response.status_code == 200, (
            'Проверьте, что на `/api/books/{book.id}/` при запросе без токена возвращаете статус 200'
        )

    @pytest.mark.django_db(transaction=True)
    def test_books_get(self, user_client, book, another_book):
        response = user_client.get('/api/books/')
        assert response.status_code == 200, (
            'Проверьте, что при GET запросе `/api/books/` с токеном авторизации возвращается статус 200'
        )

        test_data = response.json()
        assert len(test_data) == Book.objects.count(), (
            'Проверьте, что при GET запросе на `/api/books/` без пагинации возвращается весь список статей'
        )

        book = Book.objects.all()[0]
        test_book = test_data[0]
        assert 'id' in test_book, (
            'Проверьте, что добавили `id` в список полей `fields` сериализатора модели Book'
        )
        assert 'title' in test_book, (
            'Проверьте, что добавили `title` в список полей `title` сериализатора модели Book'
        )
        assert 'description' in test_book, (
            'Проверьте, что добавили `author` в список полей `description` сериализатора модели Book'
        )
        assert 'publication_date' in test_book, (
            'Проверьте, что добавили `pub_date` в список полей `publication_date` сериализатора модели Book'
        )
        assert test_book['author'] == book.author.username, (
            'Проверьте, что `author` сериализатора модели Book возвращает имя пользователя'
        )

        assert test_book['id'] == book.id, (
            'Проверьте, что при GET запросе на `/api/books/` возвращается весь список статей'
        )

    @pytest.mark.django_db(transaction=True)
    def test_book_create(self, user_client, user, another_book):
        book_count = Book.objects.count()

        data = {}
        response = user_client.post('/api/books/', data=data)
        assert response.status_code == 400, (
            'Проверьте, что при POST запросе на `/api/books/` с не правильными данными возвращается статус 400'
        )
        data = {'title': 'The Lord of the Rings',
                "description": 'Great Book'
                }
        response = user_client.post('/api/books/', data=data)
        assert response.status_code == 201, (
            'Проверьте, что при POST запросе на /api/books/'
            ' можно создать статью с description и возвращается статус 201'
        )
        assert (
                response.json().get('author') is not None
                and response.json().get('author') == user.username
        ), (
            'Проверьте, что при POST запросе на `/api/books/` автором указывается пользователь,'
            'от имени которого сделан запрос'
        )
        test_data = response.json()
        msg_error = (
            'Проверьте, что при POST запросе на `/api/books/` возвращается словарь с данными новой статьи'
        )
        assert type(test_data) == dict, msg_error
        assert test_data.get('title') == data['title'], msg_error
        assert test_data.get('description') == data['description'], msg_error

        assert test_data.get('author') == user.username, (
            'Проверьте, что при POST запросе на `/api/books/` создается книга от авторизованного пользователя'
        )
        assert book_count + 1 == Book.objects.count(), (
            'Проверьте, что при POST запросе на `/api/books/` создается книга'
        )

    @pytest.mark.django_db(transaction=True)
    def test_book_get_current(self, user_client, book, user):
        response = user_client.get(f'/api/books/{book.id}/')

        assert response.status_code == 200, (
            'Страница `/api/books/{id}/` не найдена, проверьте этот адрес в *urls.py*'
        )

        test_data = response.json()
        assert test_data.get('title') == book.title, (
            'Проверьте, что при GET запросе `/api/books/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `title`'
        )
        assert test_data.get('author') == user.username, (
            'Проверьте, что при GET запросе `/api/books/{id}/` возвращаете данные сериализатора, '
            'не найдено или не правильное значение `author`, должно возвращать имя пользователя '
        )

    @pytest.mark.django_db(transaction=True)
    def test_book_patch_current(self, user_client, book, another_book):
        response = user_client.patch(f'/api/books/{book.id}/',
                                     data={'title': 'Поменяли название книги'})

        assert response.status_code == 200, (
            'Проверьте, что при PATCH запросе `/api/books/{id}/` возвращаете статус 200'
        )

        test_book = Book.objects.filter(id=book.id).first()

        assert test_book, (
            'Проверьте, что при PATCH запросе `/api/books/{id}/` вы не удалили book'
        )

        assert test_book.title == 'Поменяли название книги', (
            'Проверьте, что при PATCH запросе `/api/books/{id}/` вы изменяете title'
        )

        response = user_client.patch(f'/api/books/{another_book.id}/',
                                     data={'title': 'Поменяли title книги'})

        assert response.status_code == 403, (
            'Проверьте, что при PATCH запросе `/api/books/` для не своей книги возвращаете статус 403'
        )

    @pytest.mark.django_db(transaction=True)
    def test_book_delete_current(self, user_client, book, another_book):
        response = user_client.delete(f'/api/books/{book.id}/')

        assert response.status_code == 204, (
            'Проверьте, что при DELETE запросе `/api/books/{id}/` возвращаете статус 204'
        )

        test_post = Book.objects.filter(id=book.id).first()

        assert not test_post, (
            'Проверьте, что при DELETE запросе `/api/books/{id}/` вы удалили книгу'
        )

        response = user_client.delete(f'/api/books/{another_book.id}/')

        assert response.status_code == 403, (
            'Проверьте, что при DELETE запросе `/api/books/{id}/` для не своей книги возвращаете статус 403'
        )
