from django.db import models
from django.contrib.auth.models import AbstractUser
from goodBuy_shop.models import Shop
from goodBuy_web.models import User

class Want(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post_text = models.TextField()
    img = models.ImageField(upload_to='want_img/', blank=True, null=True)
    update_time = models.DateTimeField(auto_now=True)

class Want_Back(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    want = models.ForeignKey(Want, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, blank=True, null=True)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)