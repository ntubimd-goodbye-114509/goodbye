from django.db import models
from goodBuy_web.models import User
from .order import Order

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE) 
    rank = models.IntegerField()
    comment = models.TextField()
    update = models.DateTimeField(auto_now=True)