from django.db import models
from goodBuy_shop.models import Product, Shop
from goodBuy_web.models import User

# 訂單
class Pay_State(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

class Order_State(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    pay_proof = models.ImageField(upload_to='pay_proofs/', blank=True, null=True)
    pay_state = models.ForeignKey(Pay_State, on_delete=models.CASCADE)
    order_state = models.ForeignKey(Order_State, on_delete=models.CASCADE)
    second_supplement = models.TextField(blank=True, null=True)
    pay = models.DecimalField(max_digits=10, decimal_places=2)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()

class Product_Order(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    amount = models.IntegerField()

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE) 
    rank = models.IntegerField()
    comment = models.TextField()
    update = models.DateTimeField(auto_now=True)