from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    introduce = models.TextField(blank=True, null=True)
    img = models.ImageField(upload_to='user_img/', null=True, blank=True)

    def __str__(self):
        return self.username  

class Blacklist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fk_user_blacklist')
    black_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='fk_black_blacklist')
    date = models.DateTimeField(auto_now_add=True)