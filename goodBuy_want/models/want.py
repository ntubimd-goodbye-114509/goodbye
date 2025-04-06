from django.db import models
from goodBuy_web.models import User

class Want(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post_text = models.TextField()
    img = models.ImageField(upload_to='want_img/', blank=True, null=True)
    update_time = models.DateTimeField(auto_now=True)