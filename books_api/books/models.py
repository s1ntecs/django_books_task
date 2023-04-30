from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, default=None)
    description = models.TextField()
    publication_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author.username}"
