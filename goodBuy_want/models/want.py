from django.db import models
from goodBuy_web.models import User
from goodBuy_shop.models import Permission

class ActiveWantManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(permission__id__in=[1, 2])
    
class Want(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    post_text = models.TextField()
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)
    update_time = models.DateTimeField(auto_now=True)

    objects = ActiveWantManager()

    def __str__(self):
        return self.title