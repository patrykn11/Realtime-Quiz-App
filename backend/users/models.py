from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Application user used by both the REST API and WebSocket clients."""

    email = models.EmailField(unique=True)

    class Meta(AbstractUser.Meta):
        db_table = "auth_user"

    def __str__(self):
        return self.username
