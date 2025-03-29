from django.db import models
from django.contrib.auth.models import AbstractUser
from goodBuy_web.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

class Permission(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

class Shop_State(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

class Purchase_Priority(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

class Payment(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

class Shop(models.Model):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    introduce = models.TextField(blank=True, null=True)
    img = models.ImageField(upload_to='shop_images/', blank=True, null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    shop_state_id = models.ForeignKey(Shop_State, on_delete=models.CASCADE)
    permission_id = models.ForeignKey(Permission, on_delete=models.CASCADE)
    purchase_priority_id = models.ForeignKey(Purchase_Priority, on_delete=models.CASCADE)

class Shop_Payment(models.Model):
    shop_id = models.ForeignKey(Shop, on_delete=models.CASCADE)
    payment_id = models.ForeignKey(Payment, on_delete=models.CASCADE)

class Shop_Tag(models.Model):
    shop_id = models.ForeignKey(Shop, on_delete=models.CASCADE)
    tag_id = models.ForeignKey(Tag, on_delete=models.CASCADE)

class Product(models.Model):
    shop_id = models.ForeignKey(Shop, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    amount = models.IntegerField()
    introduce = models.TextField(blank=True, null=True)
    img = models.ImageField(upload_to='product_images/', blank=True, null=True)

class Tag_Collect(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

class Shop_Collect(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

class Shop_Footprints(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)