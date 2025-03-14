from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    introduce = models.TextField(blank=True, null=True)
    img = models.ImageField(upload_to='user_images/', null=True, blank=True)
    register_date = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email