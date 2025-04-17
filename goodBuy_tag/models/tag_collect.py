from django.db import models
from goodBuy_web.models import User
from .tag import Tag

class TagCollect(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'tag'], name='unique_user_tag_collect')
        ]
    
    def __str__(self):
        return self.tag