from django.db import models
from goodBuy_shop.models import Shop
from goodBuy_web.models import User
from .pay_state import PayState
from .order_state import OrderState
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    total = models.IntegerField()
    pay_proof = models.ImageField(upload_to='pay_proofs/', blank=True, null=True)
    pay_state = models.ForeignKey(PayState, on_delete=models.CASCADE)
    order_state = models.ForeignKey(OrderState, on_delete=models.CASCADE)
    second_supplement = models.IntegerField(blank=True, null=True)
    pay = models.IntegerField(blank=True, null=True)