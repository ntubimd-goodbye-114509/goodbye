from django.db import models
from goodBuy_web.models import User
from .tag import Tag

class TagCollect(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)