import pytest


@pytest.fixture
def book(user):
    from books.models import Book
    return Book.objects.create(title='Тестовая книга 1', description='Тестовое описание 1', author=user)


@pytest.fixture
def book_2(user_2):
    from books.models import Book
    return Book.objects.create(title='Тестовая книга 12342341', description='Тестовое описание 12342341', author=user_2)


@pytest.fixture
def another_book(another_user):
    from books.models import Book
    return Book.objects.create(title='Тестовая книга 2', description='Тестовое описание 2', author=another_user)
