from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=32, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username

# Django's built-in Group and Permission handle roles and permissions.
