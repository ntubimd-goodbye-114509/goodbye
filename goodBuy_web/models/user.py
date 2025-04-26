from django.db import models
from django.contrib.auth.models import AbstractUser
# -------------------------
# 使用者
# -------------------------
class User(AbstractUser):
    email = models.EmailField(unique=True)
    introduce = models.TextField(blank=True, null=True)
    img = models.ImageField(upload_to='user_img/', null=True, blank=True)

    def __str__(self):
        return self.username  
