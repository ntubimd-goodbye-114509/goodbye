from django.db import models
from goodBuy_web.models import User

class Want(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    post_text = models.TextField()
    update_time = models.DateTimeField(auto_now=True)