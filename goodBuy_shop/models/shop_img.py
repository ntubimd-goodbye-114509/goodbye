import os
from django.db import models
from goodBuy_web.models import User
from .shop import Shop

# -------------------------
# 商店圖片
# -------------------------
class ShopImg(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='images')
    img = models.ImageField(upload_to='shop_img/', blank=True, null=True)
    is_cover = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)
    update = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        if self.img and os.path.isfile(self.img.path):
            os.remove(self.img.path)
        super().delete(*args, **kwargs)

    # -------------------------
    # 更換圖片後刪除原圖片
    # -------------------------
    def save(self, *args, **kwargs):
        try:
            this = ShopImg.objects.get(id=self.id)
            if this.img != self.img and this.img and os.path.isfile(this.img.path):
                os.remove(this.img.path)
        except ShopImg.DoesNotExist:
            pass
        super().save(*args, **kwargs)