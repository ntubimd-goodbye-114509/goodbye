import os
from django.db import models
from .want import Want
# -------------------------
# 收物帖圖片
# -------------------------
class WantImg(models.Model):
    want = models.ForeignKey(Want, on_delete=models.CASCADE, related_name='images')
    img = models.ImageField(upload_to='want_img/', blank=True, null=True)
    is_cover = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)
    update = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        if self.img and os.path.isfile(self.img.path):
            os.remove(self.img.path)
        super().delete(*args, **kwargs)

    # -------------------------
    # 圖片修改則刪除原圖片
    # -------------------------
    def save(self, *args, **kwargs):
        try:
            this = WantImg.objects.get(id=self.id)
            if this.img != self.img and this.img and os.path.isfile(this.img.path):
                os.remove(this.img.path)
        except WantImg.DoesNotExist:
            pass
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.img