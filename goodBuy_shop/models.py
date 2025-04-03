from django.db import models
from goodBuy_web.models import User
from goodBuy_tag.models import Tag

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
    img = models.ImageField(upload_to='shop_img/', blank=True, null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    shop_state = models.ForeignKey(Shop_State, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    purchase_priority = models.ForeignKey(Purchase_Priority, on_delete=models.CASCADE)

class Shop_Payment(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True)
    img = models.ImageField(upload_to='payment_img/', blank=True, null=True)
    account = models.CharField(max_length=255, blank=True, null=True)

class Shop_Tag(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, blank=True)

class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    amount = models.IntegerField()
    introduce = models.TextField(blank=True, null=True)
    img = models.ImageField(upload_to='product_img/', blank=True, null=True)

    def __str__(self):
        return self.name

class Shop_Collect(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

class Shop_Footprints(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)