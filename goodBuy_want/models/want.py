from django.db import models
from goodBuy_web.models import User
from goodBuy_shop.models import Permission

class Want(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    post_text = models.TextField()
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    update_time = models.DateTimeField(auto_now=True)