from rest_framework.routers import DefaultRouter
from django.urls import include, path
from .views import (
    BookViewSet, AuthToken, set_password, UsersViewSet)

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='Books')
router.register(r'users', UsersViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path(
        'auth/token/login/',
        AuthToken.as_view(),
        name='login'),
    path(
        'users/set_password/',
        set_password,
        name='set_password'),
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
