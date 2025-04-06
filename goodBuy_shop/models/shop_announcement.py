from django.db import models
from .shop import Shop

class Shop_Announcement(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    announcement = models.TextField(blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)