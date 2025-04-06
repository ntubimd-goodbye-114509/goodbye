from django.db import models
from goodBuy_tag.models import Tag
from .shop import Shop

class ShopTag(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True, blank=True)