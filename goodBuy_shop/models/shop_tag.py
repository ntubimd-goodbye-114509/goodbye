from django.db import models
from goodBuy_tag.models import Tag
from .shop import Shop

class ShopTag(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['shop', 'tag'], name='unique_shop_tag')
        ]
    
    def __str__(self):
        return self.tag