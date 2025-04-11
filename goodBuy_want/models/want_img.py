import os
from django.db import models
from .want import Want

class wantImg(models.Model):
    want = models.ForeignKey(Want, on_delete=models.CASCADE, related_name='images')
    img = models.ImageField(upload_to='want_img/', blank=True, null=True)
    is_cover = models.BooleanField(default=False)
    position = models.PositiveIntegerField(default=0)
    update = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        if self.img and os.path.isfile(self.img.path):
            os.remove(self.img.path)
        super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        try:
            this = wantImg.objects.get(id=self.id)
            if this.img != self.img and this.img and os.path.isfile(this.img.path):
                os.remove(this.img.path)
        except wantImg.DoesNotExist:
            pass
        super().save(*args, **kwargs)