from django.db import models
from .shop import Shop
import os
from django.conf import settings

class Product(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    stock = models.IntegerField()
    amount = models.IntegerField()
    introduce = models.TextField(blank=True, null=True)
    img = models.ImageField(upload_to='product_img/', blank=True, null=True)

    def __str__(self):
        return self.name
    
    def delete(self, *args, **kwargs):
        from goodBuy_order.models import ProductOrder

        # 圖片路徑字串
        img_path_str = self.img.name  # 例如 'product_img/abc.jpg'

        # 如果 ProductOrder 沒有使用這張圖，就刪掉圖片檔案
        if img_path_str and not ProductOrder.objects.filter(product_img=img_path_str).exists():
            full_path = os.path.join(settings.MEDIA_ROOT, img_path_str)
            if os.path.isfile(full_path):
                os.remove(full_path)

        super().delete(*args, **kwargs)