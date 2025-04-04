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

    def __str__(self):
        return self.black_user  
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    nickname = models.CharField(max_length=30, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

# 有時間我再來講這個（後知後覺的流程問題
class Payment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    def __str__(self):
        return self.name 
    
class Payment_Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE)
    img = models.ImageField(upload_to='payment_img/', blank=True, null=True)
    account = models.CharField(max_length=255, blank=True, null=True)